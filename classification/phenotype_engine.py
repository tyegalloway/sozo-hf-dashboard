"""Auto-classification engine for the SOZO HF Protocol.

Classifies patients into phenotypes A-D (or None) based on
ECF trajectory checkpoints and optional Phase Angle confirmation.
"""

from utils.thresholds import DAY7_WINDOW, DAY21_WINDOW


def extract_checkpoint(df, target_window, value_col="ecf_l"):
    """Find the measurement closest to the centre of a protocol window.

    Parameters
    ----------
    df : DataFrame with 'days_from_discharge' column
    target_window : tuple (lo, hi), e.g. (5, 9)
    value_col : column name to extract

    Returns
    -------
    dict with keys: day, value, found
    """
    mask = (
        (df["days_from_discharge"] >= target_window[0])
        & (df["days_from_discharge"] <= target_window[1])
    )
    window_df = df[mask]
    if window_df.empty:
        return {"day": None, "value": None, "found": False}

    centre = (target_window[0] + target_window[1]) / 2
    closest_idx = (window_df["days_from_discharge"] - centre).abs().idxmin()
    row = window_df.loc[closest_idx]
    return {
        "day": int(row["days_from_discharge"]),
        "value": float(row[value_col]),
        "found": True,
    }


def classify_patient(df, meta, thresholds):
    """Classify a single patient into a phenotype.

    Parameters
    ----------
    df : DataFrame - single patient's time-series sorted by days_from_discharge
    meta : dict - patient metadata (must include 'readmission_day')
    thresholds : dict with keys:
        hf_dex_high_risk, day7_ecf_flag, day21_recongestion, phase_angle_low

    Returns
    -------
    dict with keys:
        phenotype: str or None ('A', 'B', 'C', 'D', None)
        phenotype_sub: str or None ('None_safe', 'None_monitored')
        label: str (e.g. 'A - Very Early Readmission')
        checkpoints: dict of checkpoint results
        flags: dict of booleans
        flag_count: int
        total_flags: int
        severity: str ('ENHANCED MONITORING', 'WATCH', or '')
        pha_message: str
    """
    readmission_day = meta.get("readmission_day")
    has_readmission = readmission_day is not None

    # --- Extract discharge values ---
    discharge_row = df[df["days_from_discharge"] == 0]
    if discharge_row.empty:
        discharge_row = df.iloc[[0]]
    discharge_hf_dex = float(discharge_row["hf_dex"].iloc[0])
    discharge_ecf = float(discharge_row["ecf_l"].iloc[0])
    discharge_pha = float(discharge_row["phase_angle"].iloc[0])

    # --- Extract checkpoints ---
    day7_ecf = extract_checkpoint(df, DAY7_WINDOW, "ecf_l")
    day7_hfdex = extract_checkpoint(df, DAY7_WINDOW, "hf_dex")
    day21_ecf = extract_checkpoint(df, DAY21_WINDOW, "ecf_l")

    # --- Calculate deltas ---
    if day7_ecf["found"] and discharge_ecf != 0:
        delta7_ecf_pct = (day7_ecf["value"] - discharge_ecf) / discharge_ecf * 100.0
    else:
        delta7_ecf_pct = None

    if day7_ecf["found"] and day21_ecf["found"] and day7_ecf["value"] != 0:
        delta7_21_ecf_pct = (
            (day21_ecf["value"] - day7_ecf["value"]) / day7_ecf["value"] * 100.0
        )
    else:
        delta7_21_ecf_pct = None

    # --- Build flags ---
    hf_dex_thresh = thresholds["hf_dex_high_risk"]
    day7_thresh = thresholds["day7_ecf_flag"]
    day21_thresh = thresholds["day21_recongestion"]
    pha_thresh = thresholds["phase_angle_low"]

    flag_discharge_high = discharge_hf_dex > hf_dex_thresh
    flag_day7_not_decongesting = (
        delta7_ecf_pct is not None and delta7_ecf_pct > day7_thresh
    )
    flag_day21_recongestion = (
        delta7_21_ecf_pct is not None and delta7_21_ecf_pct > day21_thresh
    )
    flag_pha_low = discharge_pha < pha_thresh

    flags = {
        "discharge_high_risk": flag_discharge_high,
        "day7_not_decongesting": flag_day7_not_decongesting,
        "day21_recongestion": flag_day21_recongestion,
        "pha_low": flag_pha_low,
    }

    # --- Classify (priority order: A > B > C > D > None) ---
    phenotype = None
    phenotype_sub = None

    if has_readmission and readmission_day < 7:
        phenotype = "A"
    elif has_readmission and flag_day7_not_decongesting:
        phenotype = "B"
    elif (
        delta7_ecf_pct is not None
        and delta7_ecf_pct <= day7_thresh
        and flag_day21_recongestion
    ):
        phenotype = "C"
    elif has_readmission and delta7_ecf_pct is not None and delta7_ecf_pct <= day7_thresh:
        # Readmitted but decongesting at Day 7 and no (or low) Day 21 recongestion
        phenotype = "D"
    else:
        phenotype = None
        # Sub-classify non-readmitters
        if not has_readmission:
            if (
                discharge_hf_dex <= hf_dex_thresh
                and delta7_ecf_pct is not None
                and delta7_ecf_pct <= day7_thresh
            ):
                phenotype_sub = "None_safe"
            else:
                phenotype_sub = "None_monitored"

    # --- Build label ---
    from utils.thresholds import PHENOTYPE_INFO

    if phenotype is not None:
        info = PHENOTYPE_INFO[phenotype]
        label = f"{phenotype} - {info['label']}"
        icon = info["icon"]
        color = info["color"]
    elif phenotype_sub:
        info = PHENOTYPE_INFO[phenotype_sub]
        label = info["label"]
        icon = info["icon"]
        color = info["color"]
    else:
        label = "Unclassified"
        icon = ""
        color = "#6B7280"

    # --- Phase Angle severity modifier ---
    ecf_flagged = flag_day7_not_decongesting or flag_day21_recongestion
    if ecf_flagged and flag_pha_low:
        severity = "ENHANCED MONITORING"
        pha_message = f"Discharge PhA = {discharge_pha:.1f} deg - CONFIRMS risk"
    elif ecf_flagged and not flag_pha_low:
        severity = "WATCH"
        pha_message = f"Discharge PhA = {discharge_pha:.1f} deg - Suggests lower risk"
    elif flag_pha_low:
        severity = ""
        pha_message = f"Discharge PhA = {discharge_pha:.1f} deg - Below prognostic threshold"
    else:
        severity = ""
        pha_message = f"Discharge PhA = {discharge_pha:.1f} deg - Adequate"

    # --- Count flags ---
    relevant_flags = [flag_discharge_high, flag_day7_not_decongesting, flag_day21_recongestion]
    flag_count = sum(relevant_flags)
    total_flags = len(relevant_flags)

    # --- Assemble checkpoints for summary card ---
    checkpoints = {
        "discharge": {
            "hf_dex": discharge_hf_dex,
            "ecf": discharge_ecf,
            "flagged": flag_discharge_high,
        },
        "day7": {
            "found": day7_ecf["found"],
            "day": day7_ecf["day"],
            "hf_dex": day7_hfdex["value"] if day7_hfdex["found"] else None,
            "ecf": day7_ecf["value"],
            "delta_ecf_pct": round(delta7_ecf_pct, 1) if delta7_ecf_pct is not None else None,
            "flagged": flag_day7_not_decongesting,
        },
        "day21": {
            "found": day21_ecf["found"],
            "day": day21_ecf["day"],
            "ecf": day21_ecf["value"],
            "delta_ecf_pct": round(delta7_21_ecf_pct, 1) if delta7_21_ecf_pct is not None else None,
            "flagged": flag_day21_recongestion,
        },
        "phase_angle": {
            "value": discharge_pha,
            "low": flag_pha_low,
            "message": pha_message,
        },
    }

    return {
        "phenotype": phenotype,
        "phenotype_sub": phenotype_sub,
        "label": label,
        "icon": icon,
        "color": color,
        "severity": severity,
        "pha_message": pha_message,
        "checkpoints": checkpoints,
        "flags": flags,
        "flag_count": flag_count,
        "total_flags": total_flags,
    }
