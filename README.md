The Vital Voyagers
🌐 Live Web Application:[ gch-mu.vercel.app](https://gch-mu.vercel.app/)

A robust system for heart rate detection from single-lead ECG signals that works across both HL7 aECG (XML) and custom binary formats, even in the presence of noise, motion artifacts, and signal irregularities.


🚀 Features of the Web App
Instant Analysis: Upload your ECG file and get results in seconds.

Visual Dashboard: Interactive plots for ECG strips, Heart Rate Trends, and Poincaré plots.

Detailed Metrics: View Heart Rate, Rhythm Classification (Normal/AF), and Stress State side-by-side.

Clinical Report: Generates a summary similar to the PDF report output shown below.

It supports multiple input formats (XML + Binary) and works reliably even with noise, motion artifacts, and signal distortion.


🚀 Key Features

Multi-format ECG parsing (HL7 aECG XML + Binary)

Noise-resistant signal processing pipeline

Dual R-peak detection (NeuroKit + fallback logic)

Heart rate and RR interval computation

Rhythm classification using CV & RMSSD

Atrial Fibrillation (AF) screening

Stress detection using HRV

Clinical-style ECG visualization (grid + strips)

Rolling window analysis for long-duration ECG


🧠 System Pipeline
Input ECG File (.xml / binary)
        ↓
Data Parsing & Loading
        ↓
Bandpass Filtering (0.5–40 Hz)
        ↓
R-Peak Detection
        ↓
RR Interval Computation
        ↓
Heart Rate Calculation
        ↓
Rhythm Analysis (CV, RMSSD)
        ↓
AF Detection (Irregularity + P-wave absence)
        ↓
HRV Analysis (Stress Detection)
        ↓
Visualization + Final Output


⚙️ Core Methodology
1. Signal Preprocessing
Bandpass Filter: 0.5 – 40 Hz
Removes:
Baseline drift
High-frequency noise
Z-score normalization for stability

2. R-Peak Detection
Primary: NeuroKit2
Fallback: scipy.find_peaks
Ensures robustness in noisy signals

3. Heart Rate Calculation
RR Intervals:
RR = difference between consecutive R-peaks
Heart Rate:
HR = 60 / mean(RR)

4. Signal Quality Assessment
Based on variance and amplitude
Classified as:
GOOD
NOISY
POOR

5. Rhythm Classification
Metrics used:
Coefficient of Variation (CV)
RMSSD
Output:
Normal
Irregular
Possible AF

6. Atrial Fibrillation Detection
Combines:
High RR variability
High RMSSD
Absence of P-waves
Atrial signal irregularity

7. Stress Detection (ANS-Based)
Based on HR + HRV patterns:
Condition	Interpretation
High HR + Low HRV	Stress
High HR + High HRV	Physical Activity
Low HR + High HRV	Relaxed


📊 Visualizations
The system generates:

Full ECG waveform
Zoomed ECG with R-peaks
ECG strips (clinical format)
RR interval variability graph
Heart rate trend
Poincaré plot (HRV)
FFT spectrum
Rolling window analysis graphs

🧩 Problem Mapping

✅ Problem 1: Heart Rate Detection
R-peak detection
RR interval calculation
Heart rate computation
Noise handling

✅ Problem 2: Rhythm & AF Detection
RR variability analysis
Rhythm classification
AF detection via multi-feature scoring

✅ Problem 4: Stress Detection
HRV metrics (RMSSD, SDNN)
ANS-based classification
Context-aware stress vs activity detection


📂 Input Formats

XML (HL7 aECG)
ECG samples stored in <Sample> tags
Includes sampling rate metadata
Binary Format
10-byte structure:
2 bytes → ECG value (int16)
8 bytes → timestamp (int64)


⚠️ Limitations
Not calibrated in medical units (mV)
Not clinically certified
Accuracy depends on signal quality
Short recordings reduce reliability


🔮 Future Scope
Real-time monitoring dashboard
Deep learning-based arrhythmia detection
Medical-grade calibration
Mobile/web deployment
Integration with wearable devices
🏁 Conclusion

This project delivers a complete ECG analysis pipeline that goes beyond basic heart rate detection by integrating:

Signal processing
Clinical heuristics
Behavioral insights (stress detection)

It is designed as a scalable, real-world system capable of handling continuous ECG data and providing actionable health insights.
