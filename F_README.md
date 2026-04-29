# 🫀 Smart ECG Analyzer

## Heart Rate Detection + Rhythm Analysis + Possible AF Screening

This project analyzes a **single-lead ECG signal** and automatically detects:

* Heart rate
* R-peaks
* R-R intervals
* Regular or irregular rhythm
* Possible Atrial Fibrillation (AF) patterns
* Segment-wise rhythm changes
* Long recording analysis

---

# 📌 Why This Project?

ECG signals tell us how the heart is working.

This project answers two key questions:

👉 How fast is the heart beating?
👉 Is the rhythm normal or abnormal?

It combines:

* **Problem 1 → Heart Rate Detection**
* **Problem 2 → Rhythm & AF Detection**

---

# 🧠 Simple Flow of the Code

```
Start
 ↓
User enters ECG file
 ↓
Load ECG data
 ↓
Filter signal (remove noise)
 ↓
Detect R-peaks
 ↓
Calculate R-R intervals
 ↓
Calculate heart rate
 ↓
Check rhythm (normal / irregular)
 ↓
Check P-wave & atrial activity
 ↓
Detect possible AF
 ↓
Show graphs + results
```

---

# 🧩 Code Explanation (Easy Language)

## 1. File Detection

The code checks whether the file is XML or binary.

👉 Why?
Different files need different reading methods.

---

## 2. ECG Loading

The ECG signal, time, and sampling rate are extracted.

👉 Why?
We need these to analyze the signal correctly.

---

## 3. Signal Filtering

A **bandpass filter (0.5–40 Hz)** is applied.

👉 Why?
Removes noise and keeps useful heart signal.

---

## 4. Signal Quality Check

Checks if signal is GOOD / POOR / NOISY.

👉 Why?
Bad signals can give wrong results.

---

## 5. R-Peak Detection

Finds peaks using:

```
find_peaks()
```

👉 Why?
Each R-peak = 1 heartbeat.

---

## 6. R-R Interval Calculation

```
RR = difference between consecutive peaks
```

👉 Why?
Helps measure heartbeat timing.

---

## 7. Heart Rate Calculation

```
Heart Rate = 60 / RR
```

👉 Why?
Gives BPM (beats per minute).

---

# ✅ Problem 1: Tasks Completed

| Task                    | Status | How Solved                |
| ----------------------- | ------ | ------------------------- |
| R-peak detection        | ✅      | Using `find_peaks()`      |
| Heart rate estimation   | ✅      | Using RR intervals        |
| Signal preprocessing    | ✅      | Bandpass filter           |
| Noise reduction         | ✅      | Filtering                 |
| QRS detection           | ✅      | Peak detection logic      |
| RR interval calculation | ✅      | `np.diff()`               |
| HR conversion           | ✅      | `60 / RR`                 |
| Handle noise            | ✅      | Quality check + filtering |
| Multi-hour data         | ✅      | Rolling window            |

---

# 🫀 Problem 2: Rhythm & AF Detection

## 8. Rhythm Classification

Uses:

* CV (variation)
* RMSSD

👉 Why?
Checks if rhythm is stable or irregular.

---

## 9. Segment Analysis

Divides ECG into windows.

👉 Why?
Rhythm can change over time.

---

## 10. P-Wave Check

Looks for small peaks before R-peaks.

👉 Why?
AF → P-waves are often missing.

---

## 11. Atrial Activity

Checks baseline between beats.

👉 Why?
AF → irregular noisy baseline.

---

## 12. AF Decision

Combines:

* RR variability
* RMSSD
* P-wave absence
* Atrial irregularity

👉 Final output:

| Score | Result           |
| ----- | ---------------- |
| 0     | Normal           |
| 1     | Slight irregular |
| 2     | Possible AF      |
| 3+    | Strong AF        |

---

# ✅ Problem 2: Tasks Completed

| Task                    | Status | How Solved            |
| ----------------------- | ------ | --------------------- |
| Use R-peaks             | ✅      | From Problem 1        |
| Analyze RR intervals    | ✅      | Calculated            |
| Detect regular rhythm   | ✅      | CV check              |
| Detect irregular rhythm | ✅      | CV + RMSSD            |
| Segment rhythm          | ✅      | Window-based          |
| Detect AF               | ✅      | Multi-feature scoring |
| Check RR variability    | ✅      | CV                    |
| Check P-wave absence    | ✅      | Heuristic             |
| Check atrial activity   | ✅      | Variability           |
| Auto AF detection       | ✅      | Decision logic        |
| Handle real-world noise | ✅      | Filtering + checks    |

---

# 📊 Graphs Generated

* Raw ECG
* Filtered ECG
* R-peak detection
* ECG paper-style graph
* RR interval graph
* Heart rate trend
* Histogram
* Poincaré plot
* FFT spectrum
* Rolling analysis graphs

---

# ⚙️ Installation

```
pip install numpy matplotlib scipy
```

---

# ▶️ How to Use

## Step 1: Save Code

```
main.py
```

## Step 2: Add ECG File

```
main.py
ecg_data.aecg.xml
```

## Step 3: Run

```
python main.py
```

## Step 4: Enter file

```
ecg_data.aecg.xml
```

---

# 🖥️ Example Output

```
Detected R-peaks: 10
Average Heart Rate: 78 BPM
Signal Quality: GOOD

Overall Rhythm: Irregular
CV: 0.12
RMSSD: 0.09

Advanced AF Decision: Possible AF
```

---

# 🔗 Connection Between Problems

Problem 1:

```
Detects heartbeats
```

Problem 2:

```
Analyzes heartbeat pattern
```

👉 So:

```
Problem 1 → Data
Problem 2 → Intelligence
```

---

# 🧠 Viva Explanation

The code filters the ECG signal, detects R-peaks, and calculates heart rate.
Then it checks the timing between beats to determine whether the rhythm is regular.
If the rhythm is highly irregular and lacks clear P-waves, it flags possible atrial fibrillation.

---

# 🏥 Important Note

This is a **screening tool**, not a medical diagnosis.

Doctor validation is required for real use.

---

# ⭐ Final Summary

✅ Detects heart rate
✅ Detects rhythm
✅ Flags possible AF
✅ Works on long ECG data
✅ Generates graphs

---

