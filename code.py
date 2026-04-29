import numpy as np
import matplotlib.pyplot as plt
import struct
import xml.etree.ElementTree as ET
import neurokit2 as nk
from scipy.signal import butter, filtfilt, find_peaks, savgol_filter, iirnotch
import warnings

warnings.filterwarnings("ignore")

# =========================================
# FILE TYPE DETECTION
# =========================================
def detect_file_type(filename):
    return "xml" if filename.endswith((".aecg", ".xml")) else "binary"

# =========================================
# XML PARSER
# =========================================
def parse_xml_ecg(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    values = []
    for sample in root.findall(".//Sample"):
        try:
            values.append(float(sample.text))
        except:
            pass

    values = np.array(values)

    sr_elem = root.find(".//SamplingRateHz")
    fs = float(sr_elem.text) if sr_elem is not None else 250

    timestamps = np.arange(len(values)) / fs

    return values, timestamps, fs

# =========================================
# BINARY PARSER
# =========================================
def parse_binary_ecg(filename):
    values, timestamps = [], []

    with open(filename, "rb") as f:
        while True:
            chunk = f.read(10)
            if len(chunk) < 10:
                break

            values.append(struct.unpack("<h", chunk[0:2])[0])
            timestamps.append(struct.unpack("<q", chunk[2:10])[0])

    return np.array(values), np.array(timestamps)

# =========================================
# SAMPLING RATE
# =========================================
def estimate_sampling_rate(timestamps):
    if len(timestamps) < 2:
        return 250
    diffs = np.diff(timestamps)
    diffs = diffs[diffs > 0]
    return int(1000 / np.mean(diffs)) if len(diffs) else 250

# =========================================
# STRONG FILTER
# =========================================
def strong_ecg_filter(signal, fs):
    b, a = butter(4, 0.5/(0.5*fs), btype='high')
    signal = filtfilt(b, a, signal)

    b, a = butter(4, 40/(0.5*fs), btype='low')
    signal = filtfilt(b, a, signal)

    b, a = iirnotch(50/(0.5*fs), 30)
    signal = filtfilt(b, a, signal)

    return signal

# =========================================
# ANALYSIS
# =========================================
def smart_ecg_analysis(ecg_signal, fs):

    filtered = strong_ecg_filter(ecg_signal, fs)

    # Normalize
    if np.std(filtered) != 0:
        filtered = (filtered - np.mean(filtered)) / np.std(filtered)

    try:
        _, info = nk.ecg_process(filtered, sampling_rate=fs)
        r_peaks = info["ECG_R_Peaks"]
    except:
        peaks, _ = find_peaks(filtered, distance=int(0.4*fs), height=0.5)
        r_peaks = peaks

    if len(r_peaks) < 2:
        return 0, "POOR", "UNSTABLE", "NO PEAKS", r_peaks, filtered

    rr = np.diff(r_peaks) / fs
    clean_rr = [r for r in rr if 0.4 < r < 1.5]

    if len(clean_rr) == 0:
        return 0, "POOR", "UNSTABLE", "INVALID RR", r_peaks, filtered

    hr = 60 / np.mean(clean_rr)

    quality = "GOOD" if np.var(filtered) > 0.5 else "POOR"
    stability = "STABLE" if np.std(clean_rr)*60 < 5 else "FLUCTUATING"

    if quality == "POOR":
        status = "CHECK SIGNAL"
    elif hr < 60 or hr > 100:
        status = "ABNORMAL HR"
    elif stability == "FLUCTUATING":
        status = "IRREGULAR RHYTHM"
    else:
        status = "NORMAL"

    return hr, quality, stability, status, r_peaks, filtered

# =========================================
# HOSPITAL ECG PLOT (mV calibrated)
# =========================================
def plot_ecg_hospital(signal, r_peaks, fs):

    # Convert to pseudo mV
    signal_mV = signal / np.max(np.abs(signal))

    time = np.arange(len(signal)) / fs

    plt.figure(figsize=(15,5))
    ax = plt.gca()

    ax.plot(time, signal_mV, color='black', linewidth=1)

    if len(r_peaks) > 0:
        ax.scatter(np.array(r_peaks)/fs, signal_mV[r_peaks], color='red', s=25)

    # ECG grid
    ax.set_xticks(np.arange(0, time[-1], 0.04), minor=True)
    ax.set_xticks(np.arange(0, time[-1], 0.2))

    ax.set_yticks(np.arange(-2, 2, 0.1), minor=True)
    ax.set_yticks(np.arange(-2, 2, 0.5))

    ax.grid(which='minor', color='lightcoral', linewidth=0.5)
    ax.grid(which='major', color='red', linewidth=1)

    if len(time) > fs*5:
        ax.set_xlim(0,5)

    ax.set_title("ECG Monitor (Calibrated: 25 mm/s, 10 mm/mV)")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Amplitude (mV approx)")

    plt.tight_layout()
    plt.show()

# =========================================
# MAIN
# =========================================
filename = input("Enter ECG file path: ")

file_type = detect_file_type(filename)

if file_type == "xml":
    ecg_signal, timestamps, fs = parse_xml_ecg(filename)
else:
    ecg_signal, timestamps = parse_binary_ecg(filename)
    fs = estimate_sampling_rate(timestamps)

print("File Type:", file_type)
print("Sampling Rate:", fs)

hr, quality, stability, status, r_peaks, filtered = smart_ecg_analysis(ecg_signal, fs)

print("\n--- ECG ANALYSIS ---")
print("Heart Rate:", round(hr,2), "BPM")
print("Signal Quality:", quality)
print("Stability:", stability)
print("Status:", status)

plot_ecg_hospital(filtered, r_peaks, fs)