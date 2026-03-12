"""Protocol constants, thresholds, and colour definitions for the SOZO HF Dashboard."""

# ---------------------------------------------------------------------------
# Default protocol thresholds (sidebar sliders override these at runtime)
# ---------------------------------------------------------------------------
DEFAULT_THRESHOLDS = {
    "hf_dex_high_risk": 51.0,       # HF-Dex > 51% = HIGH RISK at discharge
    "day7_ecf_flag": 3.0,           # ECF delta-7 > 3% = not decongesting (FLAG)
    "day21_recongestion": 5.0,      # ECF delta-7-21 > 5% = recongestion
    "phase_angle_low": 3.5,         # PhA < 3.5 deg = low (confirmatory risk flag)
}

# Protocol checkpoint windows (day ranges)
DAY7_WINDOW = (5, 9)       # Day 7 +/- 2 days
DAY21_WINDOW = (18, 24)    # Day 21 +/- 3 days

# ---------------------------------------------------------------------------
# Phenotype definitions
# ---------------------------------------------------------------------------
PHENOTYPE_INFO = {
    "A": {
        "label": "Very Early Readmission",
        "color": "#991B1B",    # Dark red
        "icon": "\u26A1",      # lightning
    },
    "B": {
        "label": "Never Decongesting",
        "color": "#DC2626",    # Orange-red
        "icon": "\U0001F4C8",  # chart increasing
    },
    "C": {
        "label": "Re-congestion After Initial Response",
        "color": "#F97316",    # Orange
        "icon": "\U0001F504",  # arrows circle
    },
    "D": {
        "label": "The Anomaly",
        "color": "#6B7280",    # Grey/blue
        "icon": "\u2753",      # question mark
    },
    "None_safe": {
        "label": "Safe to Clear",
        "color": "#16A34A",    # Green
        "icon": "\u2713",      # check mark
    },
    "None_monitored": {
        "label": "Monitored - Stable",
        "color": "#16A34A",    # Green
        "icon": "\u2713",      # check mark
    },
}

# ---------------------------------------------------------------------------
# Phenotype explainer text
# ---------------------------------------------------------------------------
PHENOTYPE_EXPLAINERS = {
    "A": (
        "This patient was readmitted before the Day 7 follow-up visit, making outpatient "
        "intervention impossible. The discharge HF-Dex flagged high risk, indicating the "
        "patient was discharged too congested. Protocol recommendation: For patients with "
        "HF-Dex >51% at discharge, consider a Day 3 phone check or same-week clinic visit "
        "rather than waiting for Day 7."
    ),
    "B": (
        "This patient showed no evidence of decongestion after discharge - ECF increased or "
        "remained flat through Day 7. The diuretic regimen was insufficient from the start. "
        "Protocol recommendation: Immediate diuretic dose review and adjustment, with a "
        "follow-up visit at Day 10-14."
    ),
    "C": (
        "This patient initially responded to diuretic therapy (ECF decreasing at Day 7) but "
        "then reversed course - fluid began reaccumulating before Day 21. Protocol "
        "recommendation: Urgent clinical review when Day 21 ECF increase exceeds 5% from "
        "Day 7. Evaluate for medication non-adherence, dietary indiscretion, or disease "
        "progression."
    ),
    "D": (
        "This patient showed excellent, sustained decongestion throughout the monitoring period "
        "yet was still readmitted. The cause is likely non-fluid related - arrhythmia, "
        "infection, medication adverse effect, or disease progression. BIS monitors fluid "
        "status; it cannot catch every cause of decompensation. This phenotype represents "
        "the boundary of what fluid monitoring alone can achieve."
    ),
    "None": (
        "This patient showed appropriate decongestion trajectory without readmission. If "
        "HF-Dex <=51% at discharge AND ECF decreasing at Day 7, the patient qualifies as "
        "'Safe to Clear' - a population with 0% readmission rate in the HF at Home study "
        "(n=21, 30% of cohort)."
    ),
}

# ---------------------------------------------------------------------------
# Colour palette (ImpediMed-inspired)
# ---------------------------------------------------------------------------
COLORS = {
    "primary_blue": "#0066B3",
    "dark_blue": "#003366",
    "light_blue": "#E8F4FD",
    "high_risk_red": "#DC2626",
    "flag_orange": "#F97316",
    "safe_green": "#16A34A",
    "light_green": "#DCFCE7",
    "phase_angle_purple": "#7C3AED",
    "day7_window": "rgba(249, 115, 22, 0.15)",
    "day21_window": "rgba(124, 58, 237, 0.15)",
    "readmission_line": "#DC2626",
    "threshold_line": "#DC2626",
    "ecf_line": "#0066B3",
    "icf_line": "#D4A017",
    "tbw_line": "#059669",
    "weight_line": "#6B7280",
    "phase_line": "#7C3AED",
    "background": "#FFFFFF",
    "card_bg": "#F8FAFC",
    "readmission_marker": "#F97316",
}
