# Universal Smart ECG Analyzer (Clinical-Style Visualization)

## 📌 Problem Statement

ECG data is often noisy, inconsistent, and stored in different formats. Extracting meaningful heart rate and rhythm information reliably is challenging.

---

## 🚀 Solution

This project builds a **robust ECG analysis system** that:

* Supports XML (.aecg) and binary ECG formats
* Cleans noisy signals using advanced filtering
* Detects heart rate robustly
* Visualizes ECG in **hospital-style calibrated format**

---

## ⚙️ Key Features

### 1. Multi-format ECG Parsing

* XML (HL7 aECG)
* Binary format support

---

### 2. Advanced Signal Processing

* High-pass filter → removes baseline drift
* Low-pass filter → removes noise
* Notch filter → removes 50 Hz interference

---

### 3. Robust Peak Detection

* Primary: NeuroKit-based detection
* Fallback: Custom peak detection

---

### 4. Heart Rate Analysis

* RR interval computation
* Outlier filtering
* Stable HR estimation

---

### 5. Clinical ECG Visualization

Simulates real ECG machines:

* 25 mm/sec time scaling
* 10 mm/mV amplitude scaling
* Small & large ECG grid
* Highlighted R-peaks

---

## 📊 Output

* Heart Rate (BPM)
* Signal Quality
* Stability
* Status (Normal / Abnormal / Irregular)

---

## 🧠 Design Highlights

* Robust to noisy data
* Works with short signals
* Fail-safe peak detection
* Clinically inspired visualization

---

## ⚠️ Limitations

* Uses approximate mV scaling
* Not a diagnostic medical tool
* Short signals reduce reliability

---

## 🔮 Future Work

* Pan-Tompkins implementation
* AI arrhythmia detection
* PDF ECG report generation
* Real-time monitoring system

---

## 🏁 Conclusion

This project demonstrates a **complete ECG analysis pipeline** with:

* Strong signal processing
* Reliable heart rate detection
* Professional-grade visualization

---
