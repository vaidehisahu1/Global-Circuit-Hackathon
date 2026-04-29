# 🏥 Universal Smart ECG Analyzer

A robust system for **heart rate detection from single-lead ECG signals** that works across both **HL7 aECG (XML)** and **custom binary formats**, even in the presence of noise, motion artifacts, and signal irregularities.

---

## 🚀 Problem Statement

Continuous ECG monitoring often suffers from:

* Noise and motion artifacts
* Baseline drift
* Missing or distorted waveforms
* Irregular heart rhythms over long durations

The goal is to:

> Accurately estimate heart rate from a continuous single-lead ECG signal by detecting **R-peaks** and handling real-world signal challenges.

---

## 💡 Solution Overview

This project implements a **complete ECG processing pipeline**:

### 🔬 Core Workflow

1. **Data Acquisition**

   * Supports:

     * HL7 `.aecg` / `.xml`
     * Custom binary ECG format (10-byte records)

2. **Signal Preprocessing**

   * Bandpass filtering (0.5–40 Hz)
   * Noise reduction
   * Baseline drift removal
   * Signal normalization

3. **R-Peak Detection**

   * Primary: NeuroKit2 ECG processing
   * Fallback: Custom peak detection (`scipy.find_peaks`)

4. **Heart Rate Calculation**

   * RR interval computation
   * Filtering physiologically valid intervals (0.4s–1.5s)
   * BPM estimation

5. **Signal Analysis**

   * Signal quality estimation
   * Heart rate stability analysis
   * Rhythm classification

---

## 🧠 Key Features

✅ Works on **noisy real-world ECG signals**
✅ Supports **multiple file formats**
✅ **Automatic sampling rate detection**
✅ **Fallback detection system (robust)**
✅ Handles **irregular rhythms & missing beats**
✅ Produces **clinical-style ECG visualizations**

---

## 📊 Visualizations

The system generates multiple analytical plots:

* 📈 Full ECG signal
* 🔍 Zoomed ECG with R-peaks
* 🧾 ECG strips (like hospital reports)
* ⏱ RR interval variability
* ❤️ Heart rate trend
* 🔄 Poincaré plot (HRV analysis)

All ECG plots include **realistic ECG paper grid** (1 mm / 5 mm style).

---

## 🏥 ECG Paper Simulation

To mimic real clinical output:

* Small grid: 0.04 sec (1 mm)
* Large grid: 0.2 sec (5 mm)
* Visual scaling approximates medical ECG layout

---

## 📂 Supported File Formats

### 1. XML (.aecg / HL7)

* Extracts `<Sample>` values
* Reads `<SamplingRateHz>`

### 2. Binary Format

Each record = **10 bytes**

| Bytes | Field     | Type  |
| ----- | --------- | ----- |
| 0–1   | ECG Value | int16 |
| 2–9   | Timestamp | int64 |

Sampling rate is inferred from timestamp differences.

---

## ⚙️ Installation

```bash
pip install numpy matplotlib scipy neurokit2
```

---

## ▶️ Usage

```bash
python ecg.py
```

Then provide:

```bash
Enter ECG file path: ./ecg_data.aecg.xml
```

---

## 📌 Output Example

```text
--- UNIVERSAL SMART ECG ANALYZER ---
Heart Rate: 92.28 BPM
Signal Quality: GOOD
Stability: FLUCTUATING
Status: IRREGULAR RHYTHM
```

---

## 🧪 Algorithm Details

### ✔ Preprocessing

* Bandpass filter removes:

  * Baseline drift (<0.5 Hz)
  * High-frequency noise (>40 Hz)

### ✔ R-Peak Detection

* NeuroKit2 (advanced physiological model)
* Fallback: Peak detection using:

  * Minimum distance constraint
  * Amplitude threshold

### ✔ Heart Rate

[
HR = \frac{60}{\text{mean RR interval}}
]

### ✔ Robustness Enhancements

* RR interval filtering (removes outliers)
* Fallback mechanism (prevents failure)
* Signal variance-based quality scoring

---

## 🚧 Improvements for Real-World Conditions

✔ Already implemented:

* Noise filtering
* Baseline drift removal
* Outlier RR filtering
* Fallback peak detection

⚠️ Future improvements:

* Adaptive thresholding (Pan–Tompkins)
* Motion artifact detection
* Deep learning-based arrhythmia detection
* Multi-lead ECG support

---

## ⏱ Performance on Continuous Data

* Works on long signals (multi-hour capable)
* Handles:

  * Changing heart rates
  * Irregular rhythms
  * Signal interruptions

Sliding-window style processing ensures adaptability.

---

## ⚠️ Limitations

* Approximate amplitude scaling (not true mV)
* Not calibrated to medical ECG standards
* Not a certified diagnostic tool
* Performance depends on signal quality

---

## 🏁 Conclusion

This project provides a **robust and flexible ECG heart rate detection system** capable of handling real-world signal challenges.

It successfully demonstrates:

* Signal processing pipeline
* Robust peak detection
* Clinical-style visualization
* Multi-format ECG compatibility

---

## 👨‍💻 Author

Mudit Agrawal

---

## 📌 Future Scope

* Real-time ECG monitoring UI
* Medical-grade calibration
* AI-based diagnosis
* Web dashboard integration

---

## ⭐ If you like this project

Give it a ⭐ and take it further 🚀
