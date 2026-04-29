import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

# -----------------------------
# 1. XML ECG PARSER
# -----------------------------
def read_xml_ecg(path):
    tree = ET.parse(path)
    root = tree.getroot()

    fs = 960
    time = []
    values = []

    for elem in root.iter():
        tag = elem.tag.lower()

        if "samplingratehz" in tag and elem.text:
            fs = int(float(elem.text.strip()))

        if "sample" in tag and elem.text:
            try:
                values.append(float(elem.text.strip()))
                time.append(float(elem.attrib.get("time", len(values) / fs)))
            except:
                pass

    if len(values) == 0:
        raise ValueError("No ECG sample data found in XML")

    values = np.array(values)
    time = np.array(time)

    values = (values - np.mean(values)) / (np.std(values) + 1e-6)

    return time, values, fs


# -----------------------------
# 2. FILTER
# -----------------------------
def bandpass_filter(signal, fs):
    lowcut = 0.5
    highcut = 40
    nyq = 0.5 * fs

    b, a = butter(2, [lowcut / nyq, highcut / nyq], btype="band")
    return filtfilt(b, a, signal)


# -----------------------------
# 3. R PEAK DETECTION
# -----------------------------
def detect_r_peaks(signal, fs):
    height = np.mean(signal) + 0.7 * np.std(signal)

    peaks, properties = find_peaks(
        signal,
        height=height,
        distance=int(0.25 * fs),
        prominence=0.5
    )

    return peaks


# -----------------------------
# 4. RR AND HR
# -----------------------------
def compute_rr(peaks, time):
    if len(peaks) < 2:
        return None, None

    rr = np.diff(time[peaks])
    hr = 60 / rr

    return rr, hr


# -----------------------------
# 5. SEGMENT-WISE RHYTHM ANALYSIS
# -----------------------------
def analyze_segments(time, signal, peaks, rr, window_sec=10):
    results = []

    if rr is None:
        return results

    peak_times = time[peaks]

    start = time[0]
    end = time[-1]

    current = start

    while current < end:
        seg_start = current
        seg_end = current + window_sec

        idx = np.where((peak_times[:-1] >= seg_start) & (peak_times[:-1] < seg_end))[0]
        seg_rr = rr[idx]

        if len(seg_rr) >= 3:
            mean_rr = np.mean(seg_rr)
            sdnn = np.std(seg_rr)
            rmssd = np.sqrt(np.mean(np.diff(seg_rr) ** 2))
            cv = sdnn / mean_rr

            if cv < 0.08:
                label = "Normal rhythm"
            elif cv >= 0.15 and rmssd > 0.08:
                label = "Possible AF / irregularly irregular"
            else:
                label = "Irregular rhythm"

            results.append({
                "start": seg_start,
                "end": seg_end,
                "beats": len(seg_rr) + 1,
                "mean_rr": mean_rr,
                "cv": cv,
                "rmssd": rmssd,
                "label": label
            })

        current += window_sec

    return results


# -----------------------------
# 6. OVERALL CLASSIFICATION
# -----------------------------
def classify_overall(rr):
    if rr is None or len(rr) < 3:
        return "Too few R-peaks detected"

    cv = np.std(rr) / np.mean(rr)
    rmssd = np.sqrt(np.mean(np.diff(rr) ** 2))

    if cv < 0.08:
        return "Overall rhythm appears regular / normal"
    elif cv >= 0.15 and rmssd > 0.08:
        return "Overall rhythm may be consistent with possible AF"
    else:
        return "Overall rhythm is irregular but not enough evidence for AF"


# -----------------------------
# 7. MAIN ANALYSIS
# -----------------------------
def analyze_ecg(time, signal, fs):
    filtered = bandpass_filter(signal, fs)
    peaks = detect_r_peaks(filtered, fs)

    rr, hr = compute_rr(peaks, time)
    overall_label = classify_overall(rr)

    segments = analyze_segments(time, filtered, peaks, rr, window_sec=10)

    print("Signal duration:", round(time[-1], 2), "seconds")
    print("Sampling rate:", fs)
    print("Detected R-peaks:", len(peaks))
    print("Overall classification:", overall_label)

    if rr is not None:
        print("Mean HR:", round(np.mean(hr), 2), "bpm")
        print("RR CV:", round(np.std(rr) / np.mean(rr), 3))

    print("\nSegment-wise result:")
    for seg in segments:
        print(
            f"{seg['start']:.1f}s - {seg['end']:.1f}s | "
            f"CV={seg['cv']:.3f}, RMSSD={seg['rmssd']:.3f} | "
            f"{seg['label']}"
        )

    return filtered, peaks, rr, hr, overall_label, segments


# -----------------------------
# 8. PLOTS
# -----------------------------
def plot_results(time, signal, filtered, peaks, rr, hr):
    plt.figure(figsize=(12, 4))
    plt.plot(time, signal)
    plt.title("Raw ECG Signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.figure(figsize=(12, 4))
    plt.plot(time, filtered)
    plt.plot(time[peaks], filtered[peaks], "rx")
    plt.title("Filtered ECG with Detected R-Peaks")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)

    if rr is not None:
        plt.figure(figsize=(10, 4))
        plt.plot(rr, marker="o")
        plt.title("R-R Intervals")
        plt.xlabel("Beat Index")
        plt.ylabel("RR Interval (seconds)")
        plt.grid(True)

        plt.figure(figsize=(10, 4))
        plt.plot(hr, marker="o")
        plt.title("Instantaneous Heart Rate")
        plt.xlabel("Beat Index")
        plt.ylabel("Heart Rate (bpm)")
        plt.grid(True)

        plt.figure(figsize=(8, 4))
        plt.hist(rr, bins=20)
        plt.title("RR Interval Distribution")
        plt.xlabel("RR Interval (seconds)")
        plt.ylabel("Count")
        plt.grid(True)

    freqs = np.fft.rfftfreq(len(signal), d=1/fs)
    fft_vals = np.abs(np.fft.rfft(signal))

    plt.figure(figsize=(10, 4))
    plt.plot(freqs, fft_vals)
    plt.xlim(0, 50)
    plt.title("FFT Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    plt.show()


# -----------------------------
# 9. RUN
# -----------------------------
if __name__ == "__main__":
    file_path = "ecg_data.aecg.xml"

    time, signal, fs = read_xml_ecg(file_path)

    filtered, peaks, rr, hr, label, segments = analyze_ecg(time, signal, fs)

    plot_results(time, signal, filtered, peaks, rr, hr)