import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import struct
import io
import base64
import json
import datetime

from scipy.signal import butter, filtfilt, find_peaks, savgol_filter

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', transparent=True, dpi=120)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_b64

# =========================================================
# 1. FILE TYPE DETECTION
# =========================================================
def detect_file_type(filename):
    if filename.endswith((".xml", ".aecg")):
        return "xml"
    return "binary"

# =========================================================
# 2. XML ECG PARSER
# =========================================================
def parse_xml_ecg(file_obj):
    tree = ET.parse(file_obj)
    root = tree.getroot()

    values = []
    times = []

    fs = 250

    sr = root.find(".//SamplingRateHz")
    if sr is not None:
        fs = float(sr.text)

    for sample in root.findall(".//Sample"):
        try:
            values.append(float(sample.text))
            if "time" in sample.attrib:
                times.append(float(sample.attrib["time"]))
            else:
                times.append(len(values) / fs)
        except:
            pass

    values = np.array(values)
    times = np.array(times)

    if len(values) == 0:
        raise ValueError("No ECG samples found in XML file")

    return values, times, fs

# =========================================================
# 3. BINARY ECG PARSER
# =========================================================
def parse_binary_ecg(file_obj):
    values = []
    timestamps = []

    while True:
        chunk = file_obj.read(10)
        if len(chunk) < 10:
            break
        values.append(struct.unpack("<h", chunk[:2])[0])
        timestamps.append(struct.unpack("<q", chunk[2:])[0])

    values = np.array(values)
    timestamps = np.array(timestamps)

    fs = estimate_sampling_rate(timestamps)
    time = np.arange(len(values)) / fs

    return values, time, fs

# =========================================================
# 4. SAMPLING RATE ESTIMATION
# =========================================================
def estimate_sampling_rate(timestamps):
    if len(timestamps) < 2:
        return 250
    diffs = np.diff(timestamps)
    diffs = diffs[diffs > 0]
    if len(diffs) == 0:
        return 250
    return int(1000 / np.mean(diffs))

# =========================================================
# 5. ECG LOADER
# =========================================================
def load_ecg_from_bytes(file_bytes, filename):
    file_type = detect_file_type(filename)
    file_obj = io.BytesIO(file_bytes)

    if file_type == "xml":
        signal, time, fs = parse_xml_ecg(file_obj)
    else:
        signal, time, fs = parse_binary_ecg(file_obj)
    return signal, time, fs

# =========================================================
# 6. BANDPASS FILTER
# =========================================================
def bandpass_filter(signal, fs, low=0.5, high=40):
    nyq = 0.5 * fs
    if high >= nyq:
        high = nyq - 1
    b, a = butter(2, [low / nyq, high / nyq], btype="band")
    return filtfilt(b, a, signal)

# =========================================================
# 7. SIGNAL QUALITY CHECK
# =========================================================
def signal_quality_index(signal):
    std_val = np.std(signal)
    max_val = np.max(np.abs(signal))
    if std_val < 0.05:
        return "POOR"
    if max_val > 8 * std_val:
        return "NOISY"
    return "GOOD"

# =========================================================
# 8. SMART ECG ANALYSIS - PROBLEM 1 CORE
# =========================================================
def smart_ecg_analysis(ecg_signal, fs):
    filtered = bandpass_filter(ecg_signal, fs)
    filtered = (filtered - np.mean(filtered)) / (np.std(filtered) + 1e-8)
    quality = signal_quality_index(filtered)
    height_threshold = np.mean(filtered) + 0.7 * np.std(filtered)

    r_peaks, properties = find_peaks(
        filtered,
        height=height_threshold,
        distance=int(0.3 * fs),
        prominence=0.5
    )

    if len(r_peaks) < 2:
        return {
            "filtered": filtered,
            "r_peaks": r_peaks,
            "rr": None,
            "hr_series": None,
            "avg_hr": 0,
            "quality": quality,
            "status": "NO PEAKS DETECTED"
        }

    rr = np.diff(r_peaks) / fs
    clean_rr = rr[(rr > 0.3) & (rr < 2.0)]

    if len(clean_rr) == 0:
        return {
            "filtered": filtered,
            "r_peaks": r_peaks,
            "rr": rr,
            "hr_series": None,
            "avg_hr": 0,
            "quality": quality,
            "status": "INVALID RR INTERVALS"
        }

    hr_series = 60 / clean_rr
    avg_hr = 60 / np.mean(clean_rr)

    if avg_hr < 60:
        status = "LOW HEART RATE"
    elif avg_hr > 100:
        status = "HIGH HEART RATE"
    else:
        status = "NORMAL HEART RATE"

    return {
        "filtered": filtered,
        "r_peaks": r_peaks,
        "rr": rr,
        "hr_series": hr_series,
        "avg_hr": avg_hr,
        "quality": quality,
        "status": status
    }

# =========================================================
# 9. RHYTHM CLASSIFICATION - PROBLEM 2 CORE
# =========================================================
def classify_rhythm(rr):
    if rr is None or len(rr) < 3:
        return "Too few beats for rhythm analysis", 0, 0

    mean_rr = np.mean(rr)
    sdnn = np.std(rr)
    rmssd = np.sqrt(np.mean(np.diff(rr) ** 2))
    cv = sdnn / mean_rr

    if cv < 0.08:
        label = "Normal Rhythm"
    elif cv >= 0.15 and rmssd > 0.08:
        label = "Possible AF / Irregularly Irregular Rhythm"
    else:
        label = "Irregular Rhythm"

    return label, cv, rmssd

# =========================================================
# 10. SEGMENT-WISE ANALYSIS
# =========================================================
def segment_wise_analysis(r_peaks, fs, total_duration, window_sec=10):
    results = []
    if len(r_peaks) < 2:
        return results

    peak_times = r_peaks / fs
    rr = np.diff(r_peaks) / fs
    start = 0

    while start < total_duration:
        end = start + window_sec
        idx = np.where((peak_times[:-1] >= start) & (peak_times[:-1] < end))[0]
        seg_rr = rr[idx]

        if len(seg_rr) >= 3:
            label, cv, rmssd = classify_rhythm(seg_rr)
            results.append({
                "start": start,
                "end": min(end, total_duration),
                "beats": len(seg_rr) + 1,
                "mean_rr": np.mean(seg_rr),
                "mean_hr": 60 / np.mean(seg_rr),
                "cv": cv,
                "rmssd": rmssd,
                "label": label
            })
        start += window_sec
    return results

# =========================================================
# 11. P-WAVE DETECTION HEURISTIC
# =========================================================
def detect_p_wave_evidence(filtered, r_peaks, fs):
    if len(r_peaks) < 3:
        return 0, "Insufficient beats for P-wave analysis"

    p_detected = 0
    checked = 0

    for r in r_peaks:
        start = int(r - 0.25 * fs)
        end = int(r - 0.08 * fs)
        if start < 0 or end <= start:
            continue
        segment = filtered[start:end]
        checked += 1
        if len(segment) < 5:
            continue
        local_peaks, _ = find_peaks(
            segment,
            height=np.mean(segment) + 0.15 * np.std(segment),
            prominence=0.05
        )
        if len(local_peaks) > 0:
            p_detected += 1

    if checked == 0:
        return 0, "P-wave region not available"

    p_wave_ratio = p_detected / checked

    if p_wave_ratio > 0.6:
        label = "Repeated P-waves likely present"
    elif p_wave_ratio < 0.3:
        label = "Repeated P-waves likely absent"
    else:
        label = "P-wave evidence unclear"
    return p_wave_ratio, label

# =========================================================
# 12. ATRIAL ACTIVITY ANALYSIS
# =========================================================
def atrial_activity_analysis(filtered, r_peaks, fs):
    if len(r_peaks) < 3:
        return 0, "Insufficient beats for atrial activity analysis"

    atrial_segments = []
    for i in range(len(r_peaks) - 1):
        start = int(r_peaks[i] + 0.12 * fs)
        end = int(r_peaks[i + 1] - 0.12 * fs)
        if end > start and end < len(filtered):
            atrial_segments.extend(filtered[start:end])

    atrial_segments = np.array(atrial_segments)
    if len(atrial_segments) < fs * 0.5:
        return 0, "Atrial segment too short"

    atrial_variability = np.std(atrial_segments)
    if atrial_variability > 0.45:
        label = "Disorganized atrial activity likely"
    else:
        label = "Atrial activity appears relatively organized"
    return atrial_variability, label

# =========================================================
# 13. ADVANCED AF DECISION
# =========================================================
def advanced_af_decision(rr, p_wave_ratio, atrial_variability):
    if rr is None or len(rr) < 3:
        return "Too few beats for AF decision"

    mean_rr = np.mean(rr)
    cv = np.std(rr) / mean_rr
    rmssd = np.sqrt(np.mean(np.diff(rr) ** 2))

    score = 0
    if cv >= 0.15:
        score += 1
    if rmssd > 0.08:
        score += 1
    if p_wave_ratio < 0.3:
        score += 1
    if atrial_variability > 0.45:
        score += 1

    if score >= 3:
        return "Strong Possible AF"
    elif score == 2:
        return "Possible AF"
    elif score == 1:
        return "Irregular / Needs Review"
    else:
        return "Normal Rhythm Likely"

# =========================================================
# 14. ROLLING WINDOW ANALYSIS
# =========================================================
def rolling_window_analysis(ecg_signal, fs, window_sec=30, step_sec=10):
    window = int(window_sec * fs)
    step = int(step_sec * fs)
    rolling_results = []

    if len(ecg_signal) < window:
        return rolling_results

    for start in range(0, len(ecg_signal) - window + 1, step):
        end = start + window
        segment = ecg_signal[start:end]

        result = smart_ecg_analysis(segment, fs)
        rr = result["rr"]
        r_peaks = result["r_peaks"]
        filtered = result["filtered"]

        rhythm_label, cv, rmssd = classify_rhythm(rr)
        p_ratio, p_label = detect_p_wave_evidence(filtered, r_peaks, fs)
        atrial_var, atrial_label = atrial_activity_analysis(filtered, r_peaks, fs)
        af_label = advanced_af_decision(rr, p_ratio, atrial_var)

        rolling_results.append({
            "start_sec": start / fs,
            "end_sec": end / fs,
            "avg_hr": result["avg_hr"],
            "quality": result["quality"],
            "rhythm": rhythm_label,
            "cv": cv,
            "rmssd": rmssd,
            "p_wave_ratio": p_ratio,
            "p_wave_label": p_label,
            "atrial_variability": atrial_var,
            "atrial_label": atrial_label,
            "af_decision": af_label
        })

    return rolling_results

# =========================================================
# 15. ECG PAPER GRID
# =========================================================
def add_ecg_grid(ax):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    for x in np.arange(xmin, xmax, 0.04):
        ax.axvline(x, color="lightcoral", lw=0.3, alpha=0.25)
    for x in np.arange(xmin, xmax, 0.2):
        ax.axvline(x, color="red", lw=0.7, alpha=0.35)
    for y in np.arange(ymin, ymax, 0.1):
        ax.axhline(y, color="lightcoral", lw=0.3, alpha=0.25)
    for y in np.arange(ymin, ymax, 0.5):
        ax.axhline(y, color="red", lw=0.7, alpha=0.35)

# =========================================================
# 16. GENERATE ALL GRAPHS AS BASE64
# =========================================================
def generate_graphs(raw_signal, filtered, r_peaks, rr, hr_series, fs):
    images = {}
    time = np.arange(len(raw_signal)) / fs
    smooth = filtered / (np.max(np.abs(filtered)) + 1e-8)
    if len(smooth) > 31:
        smooth = savgol_filter(smooth, 31, 2)

    # Luxury Theme Colors
    color_line = "#0F2C59" # Deep Navy
    color_accent1 = "#8B9A8D" # Sage Green
    color_accent2 = "#C5A880" # Soft Gold
    color_text = "#1A1A1A"
    color_grid = "#E5E5E5"

    # 1. Raw ECG Signal
    fig = plt.figure(figsize=(10, 3))
    plt.plot(time, raw_signal, color=color_line, linewidth=0.8)
    plt.title("RAW SIGNAL", color=color_text, fontsize=10, pad=15)
    plt.xlabel("Time (s)", color=color_text, fontsize=8)
    plt.ylabel("Amplitude", color=color_text, fontsize=8)
    plt.grid(True, linestyle="-", color=color_grid, alpha=0.5)
    plt.tick_params(colors=color_text, labelsize=8)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color(color_grid)
    plt.gca().spines['bottom'].set_color(color_grid)
    plt.tight_layout()
    images["raw_ecg"] = fig_to_base64(fig)

    # 2. Filtered ECG Signal
    fig = plt.figure(figsize=(10, 3))
    plt.plot(time, filtered, color=color_line, linewidth=0.8)
    plt.title("FILTERED SIGNAL", color=color_text, fontsize=10, pad=15)
    plt.xlabel("Time (s)", color=color_text, fontsize=8)
    plt.ylabel("Normalized", color=color_text, fontsize=8)
    plt.grid(True, linestyle="-", color=color_grid, alpha=0.5)
    plt.tick_params(colors=color_text, labelsize=8)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color(color_grid)
    plt.gca().spines['bottom'].set_color(color_grid)
    plt.tight_layout()
    images["filtered_ecg"] = fig_to_base64(fig)

    # 3. R-Peak Detection
    fig = plt.figure(figsize=(10, 3))
    plt.plot(time, filtered, color=color_line, linewidth=0.8)
    if len(r_peaks) > 0:
        plt.scatter(r_peaks / fs, filtered[r_peaks], color=color_accent2, s=25, label="R-peaks", zorder=3)
    plt.title("R-PEAK DETECTION", color=color_text, fontsize=10, pad=15)
    plt.xlabel("Time (s)", color=color_text, fontsize=8)
    plt.ylabel("Amplitude", color=color_text, fontsize=8)
    plt.legend(frameon=False, fontsize=8)
    plt.grid(True, linestyle="-", color=color_grid, alpha=0.5)
    plt.tick_params(colors=color_text, labelsize=8)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color(color_grid)
    plt.gca().spines['bottom'].set_color(color_grid)
    plt.tight_layout()
    images["r_peaks"] = fig_to_base64(fig)

    # 4. ECG Paper Style
    fig = plt.figure(figsize=(10, 3))
    plt.plot(time, smooth, color=color_line, linewidth=0.8)
    if len(r_peaks) > 0:
        plt.scatter(r_peaks / fs, smooth[r_peaks], color=color_accent1, s=20, zorder=3)
    plt.title("STANDARD TRACING", color=color_text, fontsize=10, pad=15)
    plt.xlabel("Time (s)", color=color_text, fontsize=8)
    plt.ylabel("Amplitude", color=color_text, fontsize=8)
    ax = plt.gca()
    add_ecg_grid(ax)
    plt.tick_params(colors=color_text, labelsize=8)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.tight_layout()
    images["ecg_paper"] = fig_to_base64(fig)

    if rr is not None:
        # RR Interval Variation
        fig = plt.figure(figsize=(8, 3))
        plt.plot(rr, marker="o", markersize=4, color=color_accent1, linestyle="-", linewidth=1)
        plt.title("R-R INTERVAL VARIATION", color=color_text, fontsize=10, pad=15)
        plt.xlabel("Beat Index", color=color_text, fontsize=8)
        plt.ylabel("RR (s)", color=color_text, fontsize=8)
        plt.grid(True, linestyle="-", color=color_grid, alpha=0.5)
        plt.tick_params(colors=color_text, labelsize=8)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_color(color_grid)
        plt.gca().spines['bottom'].set_color(color_grid)
        plt.tight_layout()
        images["rr_interval"] = fig_to_base64(fig)

        # RR Interval Distribution
        fig = plt.figure(figsize=(6, 3))
        plt.hist(rr, bins=20, color=color_line, alpha=0.8, edgecolor="white")
        plt.title("RR DISTRIBUTION", color=color_text, fontsize=10, pad=15)
        plt.xlabel("RR (s)", color=color_text, fontsize=8)
        plt.ylabel("Count", color=color_text, fontsize=8)
        plt.grid(True, linestyle="-", color=color_grid, alpha=0.5)
        plt.tick_params(colors=color_text, labelsize=8)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_color(color_grid)
        plt.gca().spines['bottom'].set_color(color_grid)
        plt.tight_layout()
        images["rr_dist"] = fig_to_base64(fig)

        # Poincaré Plot
        if len(rr) > 2:
            fig = plt.figure(figsize=(4, 4))
            plt.scatter(rr[:-1], rr[1:], color=color_accent2, alpha=0.8, s=20)
            plt.title("POINCARÉ PLOT", color=color_text, fontsize=10, pad=15)
            plt.xlabel("RR(n)", color=color_text, fontsize=8)
            plt.ylabel("RR(n+1)", color=color_text, fontsize=8)
            plt.grid(True, linestyle="-", color=color_grid, alpha=0.5)
            plt.tick_params(colors=color_text, labelsize=8)
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['left'].set_color(color_grid)
            plt.gca().spines['bottom'].set_color(color_grid)
            plt.tight_layout()
            images["poincare"] = fig_to_base64(fig)

    if hr_series is not None:
        fig = plt.figure(figsize=(8, 3))
        plt.plot(hr_series, marker="o", markersize=4, color=color_line, linestyle="-", linewidth=1)
        plt.axhline(60, linestyle="--", color=color_grid, label="60 BPM")
        plt.axhline(100, linestyle="--", color=color_grid, label="100 BPM")
        plt.title("HEART RATE TREND", color=color_text, fontsize=10, pad=15)
        plt.xlabel("Beat Index", color=color_text, fontsize=8)
        plt.ylabel("HR (BPM)", color=color_text, fontsize=8)
        plt.legend(frameon=False, fontsize=8)
        plt.grid(True, linestyle="-", color=color_grid, alpha=0.5)
        plt.tick_params(colors=color_text, labelsize=8)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_color(color_grid)
        plt.gca().spines['bottom'].set_color(color_grid)
        plt.tight_layout()
        images["hr_trend"] = fig_to_base64(fig)

    return images

# =========================================================
# 17. PROBLEM 4: STRESS DETECTION LOGIC
# =========================================================
def calculate_hrv_metrics(r_peaks, fs):
    rr_intervals = np.diff(r_peaks) / fs
    if len(rr_intervals) < 2:
        return 0, 0, 0, rr_intervals
    sdnn = np.std(rr_intervals)
    diff_rr = np.diff(rr_intervals)
    rmssd = np.sqrt(np.mean(diff_rr ** 2))
    mean_rr = np.mean(rr_intervals)
    return mean_rr, sdnn, rmssd, rr_intervals

def detect_stress_state_advanced(hr, rmssd, rr_intervals, quality, current_time=None):
    if quality == "POOR":
        return "CANNOT ASSESS (Poor Signal)", 0.0

    if current_time is None:
        current_time = datetime.datetime.now().time()
    
    hour = current_time.hour
    is_sleep_time = (hour >= 23) or (hour < 6)

    if len(rr_intervals) > 1:
        mean_rr = np.mean(rr_intervals)
        std_rr = np.std(rr_intervals)
        cv = std_rr / mean_rr
    else:
        cv = 0

    if is_sleep_time:
        if hr > 100: 
            return "UNUSUAL NIGHTTIME HR", 0.9
        else:
            return "SLEEP / REST STATE", 0.95

    if hr > 90 and cv < 0.05:
        return "HIGH STRESS", 0.90
    elif hr > 90 and cv > 0.10:
        return "ACTIVE / HIGH ENERGY", 0.80
    elif hr < 75 and rmssd > 0.050:
        return "RELAXED", 0.90
    else:
        return "NORMAL / NEUTRAL", 0.70

# =========================================================
# 18. FINAL COMBINED PIPELINE
# =========================================================
def process_ecg_data(file_bytes, filename):
    raw_signal, time, fs = load_ecg_from_bytes(file_bytes, filename)
    
    # Check length
    duration = len(raw_signal) / fs
    
    result = smart_ecg_analysis(raw_signal, fs)
    filtered = result["filtered"]
    r_peaks = result["r_peaks"]
    rr = result["rr"]
    hr_series = result["hr_series"]
    avg_hr = result["avg_hr"]
    quality = result["quality"]
    status = result["status"]

    rhythm_label, cv, rmssd = classify_rhythm(rr)
    total_duration = len(raw_signal) / fs
    segments = segment_wise_analysis(r_peaks, fs, total_duration, window_sec=10)

    p_wave_ratio, p_wave_label = detect_p_wave_evidence(filtered, r_peaks, fs)
    atrial_variability, atrial_label = atrial_activity_analysis(filtered, r_peaks, fs)
    advanced_af_label = advanced_af_decision(rr, p_wave_ratio, atrial_variability)

    # Stress Analysis
    mean_rr, sdnn, stress_rmssd, rr_intervals = calculate_hrv_metrics(r_peaks, fs)
    stress_state, stress_confidence = detect_stress_state_advanced(avg_hr, stress_rmssd, rr_intervals, quality)

    # Convert floats for JSON serialization
    safe_avg_hr = float(avg_hr) if not np.isnan(avg_hr) else 0.0
    safe_cv = float(cv) if not np.isnan(cv) else 0.0
    safe_rmssd = float(rmssd) if not np.isnan(rmssd) else 0.0
    safe_p_wave_ratio = float(p_wave_ratio) if not np.isnan(p_wave_ratio) else 0.0
    safe_atrial_variability = float(atrial_variability) if not np.isnan(atrial_variability) else 0.0

    safe_segments = []
    for s in segments:
        safe_segments.append({
            "start": float(s["start"]),
            "end": float(s["end"]),
            "beats": int(s["beats"]),
            "mean_hr": float(s["mean_hr"]),
            "cv": float(s["cv"]),
            "rmssd": float(s["rmssd"]),
            "label": s["label"]
        })

    images = generate_graphs(raw_signal, filtered, r_peaks, rr, hr_series, fs)

    return {
        "success": True,
        "metadata": {
            "duration_sec": float(duration),
            "sampling_rate": float(fs),
            "signal_length": len(raw_signal)
        },
        "problem1": {
            "status": status,
            "avg_hr": safe_avg_hr,
            "quality": quality
        },
        "problem2": {
            "overall_rhythm": rhythm_label,
            "cv": safe_cv,
            "rmssd": safe_rmssd,
            "segments": safe_segments
        },
        "af_evidence": {
            "p_wave_ratio": safe_p_wave_ratio,
            "p_wave_label": p_wave_label,
            "atrial_variability": safe_atrial_variability,
            "atrial_activity": atrial_label,
            "decision": advanced_af_label
        },
        "stress_analysis": {
            "state": stress_state,
            "confidence": float(stress_confidence),
            "sdnn": float(sdnn) if not np.isnan(sdnn) else 0.0,
            "rmssd": float(stress_rmssd) if not np.isnan(stress_rmssd) else 0.0
        },
        "images": images
    }
