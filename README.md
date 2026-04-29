The Vital Voyagers
🌐 Live Web Application: CardioSync

A robust system for heart rate detection from single-lead ECG signals that works across both HL7 aECG (XML) and custom binary formats, even in the presence of noise, motion artifacts, and signal irregularities.

🚀 Features of the Web App
Instant Analysis: Upload your ECG file and get results in seconds.
Visual Dashboard: Interactive plots for ECG strips, Heart Rate Trends, and Poincaré plots.
Detailed Metrics: View Heart Rate, Rhythm Classification (Normal/AF), and Stress State side-by-side.
Clinical Report: Generates a summary similar to the PDF report output shown below.
📄 Sample Report Output
The web app generates a comprehensive analysis report including:

METRIC	VALUE	INTERPRETATION
Average Heart Rate	138.4 BPM	High Heart Rate
Signal Quality	GOOD	Reliable Data
Overall Rhythm	Possible AF	Irregularly Irregular
Stress State	ACTIVE / HIGH ENERGY	Not Stress (Exercise/Active)
📋 Project Overview
This project analyzes a single-lead ECG signal and automatically detects:

Heart Rate (BPM)
R-peaks (Heartbeat locations)
R-R intervals (Time between beats)
Regular or irregular rhythm
Possible Atrial Fibrillation (AF) patterns
Heart Rate Variability (HRV) metrics
Physiological Stress vs. Relaxation states
Segment-wise rhythm changes for long recordings
📌 Why This Project?
ECG signals are the gold standard for monitoring heart health, but raw signals are hard to interpret. This project transforms raw waves into actionable insights by answering three key questions:

👉 How fast is the heart beating? (Problem 1)
👉 Is the rhythm normal or abnormal? (Problem 2)
👉 Is the body stressed or relaxed? (Problem 4)
It combines signal processing, clinical logic, and autonomic nervous system analysis into a single pipeline.

🧠 Simple Flow of the Code
The system follows a logical pipeline from raw data to final diagnosis:

Start
User uploads ECG file (.xml or binary)
Load & Parse Data
Preprocessing (Bandpass Filter to remove noise)
[Problem 1] Detect R-peaks & Calculate Heart Rate
[Problem 2] Analyze R-R Intervals (Regularity)
[Problem 2] Check for AF (P-wave absence + Irregularity)
[Problem 4] Calculate HRV Metrics (RMSSD, Variability)
[Problem 4] Detect Stress State (Contextual Logic)
Check Circadian Rhythm (Sleep vs Awake)
Distinguish Physical Activity vs Mental Stress
Display Results:
Heart Rate (BPM)
Rhythm Status (Normal / AF)
Stress State (Relaxed / Stressed / Active)
Clinical Graphs (ECG Strips, Poincaré Plot)
🧩 Code Explanation (Easy Language)
1. File Detection
The code checks whether the uploaded file is XML or Binary.

Why? Different file formats store data differently. The code needs to know which "reading method" to use so it doesn't crash.

2. ECG Loading
The ECG signal values, timestamps, and sampling rate are extracted from the file.

Why? We need the raw numbers (data points) and the timing information to reconstruct the heartbeat signal on the computer.

3. Signal Filtering
A bandpass filter (0.5–40 Hz) is applied to the raw signal.

Why? Raw ECG signals are noisy (muscle movement, electrical interference). This filter removes low noise (baseline drift) and high noise (static/buzz), keeping only the clear heart signal.

4. Signal Quality Check
The code checks if the signal is GOOD, POOR, or NOISY based on variance.

Why? If the signal is bad (e.g., a loose sensor), the calculations will be wrong. This step warns the user not to trust the data if the quality is poor.

5. R-Peak Detection (Problem 1)
Finds the location of the "spikes" (R-peaks) in the ECG wave using peak detection algorithms.

Why? Each R-peak represents one heartbeat. Finding these peaks is the foundation for all other calculations.

6. R-R Interval Calculation
Calculates the time difference between two consecutive R-peaks.

Why? This tells us exactly how much time passed between two heartbeats.

7. Heart Rate Calculation (Problem 1)
Converts the intervals into Beats Per Minute (BPM).

Formula: Heart Rate = 60 / Average RR IntervalWhy? "Seconds between beats" is hard to understand. BPM is the standard.

8. Rhythm Classification (Problem 2)
Analyzes the variability of the R-R intervals.

Low Variability = Normal Rhythm.
High Variability = Irregular Rhythm / Possible AF.
Why? A healthy heart isn't a perfect metronome, but too much chaos suggests Arrhythmia.
9. Atrial Fibrillation (AF) Screening (Problem 2)
Checks for specific AF signs:

Are R-R intervals highly irregular?
Are P-waves (atrial activity) missing?
Why? AF is a dangerous condition where the upper heart chambers quiver instead of beating properly.
10. HRV Metrics Calculation (Problem 4)
Calculates Heart Rate Variability (HRV) metrics, specifically RMSSD and SDNN.

Why? HRV measures the balance between the "Fight or Flight" and "Rest and Digest" nervous systems.

11. Stress State Detection (Problem 4)
Uses a decision tree to classify the user's state:

High HR + Low Variability = Stress (Rigid heart).
High HR + High Variability = Active/Exercise (Adaptable heart).
Low HR + High Variability = Relaxed.
Why? Heart Rate alone isn't enough. A runner has a high heart rate but isn't "stressed."
✅ Problem 1: Tasks Completed
TASK	STATUS	HOW SOLVED
R-peak detection	✅	Using find_peaks()
Heart rate estimation	✅	Using RR intervals
Signal preprocessing	✅	Bandpass filter
Noise reduction	✅	Filtering
QRS detection	✅	Peak detection logic
RR interval calculation	✅	np.diff()
HR conversion	✅	60 / RR
Handle noise	✅	Quality check + filtering
Multi-hour data	✅	Rolling window
🫀 Problem 2: Rhythm & AF Detection
Rhythm Classification
Uses CV (variation) and RMSSD.

Why? Checks if rhythm is stable or irregular.

AF Decision Logic
Combines:

RR variability
RMSSD
P-wave absence
Atrial irregularity
Final Output Scoring:

SCORE	RESULT
0	Normal
1	Slight irregular
2	Possible AF
3+	Strong AF
✅ Problem 2: Tasks Completed
TASK	STATUS	HOW SOLVED
Use R-peaks	✅	From Problem 1
Analyze RR intervals	✅	Calculated
Detect regular rhythm	✅	CV check
Detect irregular rhythm	✅	CV + RMSSD
Detect AF	✅	Multi-feature scoring
P-wave absence	✅	Heuristic Check
🧠 Problem 4: Stress & ANS Detection
Stress Logic (Context-Aware)
Checks Heart Rate, Variability, and Time of Day.

Final Stress State Logic:

CONDITION	RESULT
High HR + Low Var	HIGH STRESS
High HR + High Var	ACTIVE / EXERCISE
Low HR + High Var	RELAXED
Nighttime + Low HR	SLEEP / REST
✅ Problem 4: Tasks Completed
TASK	STATUS	HOW SOLVED
Extract RR intervals	✅	From Problem 1
Calculate HRV metrics	✅	RMSSD, SDNN, CV
Detect Stress state	✅	Threshold logic
Detect Relaxed state	✅	Threshold logic
Filter Exercise	✅	Context check (Variability)
Handle Sleep	✅	Time check (Circadian)
📊 Graphs Generated
Raw ECG
Filtered ECG
R-peak detection
ECG paper-style graph
RR interval graph
Heart rate trend
Histogram
Poincaré plot (HRV Visual)
FFT spectrum
Rolling analysis graphs
⚙️ Installation
pip install numpy matplotlib scipy neurokit2
▶️ How to Use
Step 1: Save Code
Save the main script as main.py.

Step 2: Add ECG File
Place your ecg_data.aecg.xml in the same directory.

Step 3: Run

bash

python main.py
Step 4: Enter file
Input the filename when prompted:

text

ecg_data.aecg.xml
🖥️ Example Output
text

--- UNIVERSAL SMART ECG ANALYZER ---
Heart Rate: 92.28 BPM
Signal Quality: GOOD
Status: IRREGULAR RHYTHM

--- PROBLEM 4 RESULTS (ENHANCED) ---
RMSSD (Variability): 310.01 ms
Coefficient of Variation (CV): 0.301
DETECTED STATE: ACTIVE / HIGH ENERGY (Not Stress)
🔗 Connection Between Problems
Problem 1: Detects heartbeats (R-peaks).
Problem 2: Analyzes heartbeat pattern (Rhythm/AF).
Problem 4: Analyzes heartbeat variation (Stress/HRV).
Logic Flow:

Problem 1 → Data (The "What")
Problem 2 → Clinical Intelligence (The "Health")
Problem 4 → Behavioral Insight (The "State")
🏥 Important Note
This is a screening tool, not a medical diagnosis. Doctor validation is required for real use.

⭐ Final Summary
✅ Detects heart rate
✅ Detects rhythm (Regular/Irregular)
✅ Flags possible AF
✅ Detects Stress vs Relaxation
✅ Distinguishes Exercise from Stress
✅ Works on long ECG data
✅ Generates clinical graphs
