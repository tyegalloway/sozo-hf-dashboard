# SOZO HF Protocol Dashboard

Interactive fluid status tracking dashboard for heart failure patients using SOZO Pro bioimpedance spectroscopy data. Auto-classifies patients into clinical phenotypes (A-D) based on the SOZO HF Protocol.

## Quick Start

**Prerequisites:** Python 3.10 or later

**Setup (one-time):**

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt
```

**Run:**

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8502`.

## What You're Looking At

This dashboard visualises post-discharge fluid trajectories from the HF at Home study (n=83 patients, 9 readmissions). Select a patient from the sidebar to see:

- **5 time-series panels**: HF-Dex, ECF/ICF, TBW, Weight, Phase Angle
- **Protocol checkpoints**: Day 7 (+/-2d) and Day 21 (+/-3d) assessment windows
- **Auto-classification** into 4 readmission phenotypes:
  - **A** - Very Early Readmission (before Day 7)
  - **B** - Never Decongesting (ECF rising from discharge)
  - **C** - Re-congestion After Initial Response (good Day 7, bad Day 21)
  - **D** - The Anomaly (excellent decongestion, non-fluid readmission cause)

Threshold sliders in the sidebar let you explore how different cutoffs affect classification.

## Key Patients to Demo

| Patient | Phenotype | Why It's Interesting |
|---------|-----------|---------------------|
| 1702    | B         | Showcase patient - double warning (HIGH discharge + ECF rising) |
| 1012    | C         | Classic re-congestion - excellent Day 7, dramatic Day 21 reversal |
| 315     | D         | The anomaly - perfect decongestion, still readmitted |
| 702     | A         | Highest HF-Dex in cohort (56.7%), readmitted Day 3 |
| 2001    | None      | "Safe to Clear" control - standard risk, good decongestion, 0% readmit |

## Data

All data is synthetic/demo, generated from documented clinical patterns in the HF at Home study. No real patient data is included.
