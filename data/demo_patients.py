"""Synthetic demo patient data for the SOZO HF Dashboard.

Generates physiologically plausible time-series for 11 patients:
  - 9 readmitters (Phenotypes A, B, C, D)
  - 2 non-readmitter controls
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Patient metadata
# ---------------------------------------------------------------------------
PATIENT_METADATA = {
    702: {
        "patient_id": 702,
        "discharge_date": "2024-01-10",
        "discharge_hf_dex": 56.7,
        "readmission_day": 3,
        "phenotype": "A",
        "phenotype_label": "Very Early Readmission",
    },
    912: {
        "patient_id": 912,
        "discharge_date": "2024-02-05",
        "discharge_hf_dex": 51.6,
        "readmission_day": 3,
        "phenotype": "A",
        "phenotype_label": "Very Early Readmission",
    },
    1015: {
        "patient_id": 1015,
        "discharge_date": "2024-01-20",
        "discharge_hf_dex": 49.6,
        "readmission_day": 10,
        "phenotype": "B",
        "phenotype_label": "Never Decongesting",
    },
    1702: {
        "patient_id": 1702,
        "discharge_date": "2024-03-01",
        "discharge_hf_dex": 54.6,
        "readmission_day": 13,
        "phenotype": "B",
        "phenotype_label": "Never Decongesting",
    },
    504: {
        "patient_id": 504,
        "discharge_date": "2024-01-15",
        "discharge_hf_dex": 50.0,
        "readmission_day": 40,
        "phenotype": "B",
        "phenotype_label": "Never Decongesting",
    },
    918: {
        "patient_id": 918,
        "discharge_date": "2024-02-12",
        "discharge_hf_dex": 52.9,
        "readmission_day": 20,
        "phenotype": "C",
        "phenotype_label": "Re-congestion After Initial Response",
    },
    1011: {
        "patient_id": 1011,
        "discharge_date": "2024-02-28",
        "discharge_hf_dex": 50.8,
        "readmission_day": 29,
        "phenotype": "C",
        "phenotype_label": "Re-congestion After Initial Response",
    },
    1012: {
        "patient_id": 1012,
        "discharge_date": "2024-03-10",
        "discharge_hf_dex": 52.9,
        "readmission_day": 30,
        "phenotype": "C",
        "phenotype_label": "Re-congestion After Initial Response",
    },
    315: {
        "patient_id": 315,
        "discharge_date": "2024-01-25",
        "discharge_hf_dex": 52.7,
        "readmission_day": 36,
        "phenotype": "D",
        "phenotype_label": "The Anomaly",
    },
    2001: {
        "patient_id": 2001,
        "discharge_date": "2024-04-01",
        "discharge_hf_dex": 48.2,
        "readmission_day": None,
        "phenotype": None,
        "phenotype_label": "Stable / Safe to Clear",
    },
    2002: {
        "patient_id": 2002,
        "discharge_date": "2024-04-15",
        "discharge_hf_dex": 53.0,
        "readmission_day": None,
        "phenotype": None,
        "phenotype_label": "Stable / Safe to Clear",
    },
}

# ---------------------------------------------------------------------------
# Per-patient generation parameters
# ---------------------------------------------------------------------------
_PARAMS = {
    702: dict(
        base_ecf=19.5, base_icf=14.9, base_weight=88.0, base_pha=2.8,
        max_day=3,
        ecf_trend="flat_high",  # flat/slightly rising
        ecf_slope=0.05,
    ),
    912: dict(
        base_ecf=17.5, base_icf=16.4, base_weight=82.0, base_pha=3.5,
        max_day=3,
        ecf_trend="flat_high",
        ecf_slope=0.03,
    ),
    1015: dict(
        base_ecf=16.0, base_icf=16.3, base_weight=85.0, base_pha=3.1,
        max_day=10,
        ecf_trend="rising",
        ecf_slope=0.15,  # produces ~+9.3% by day 7
    ),
    1702: dict(
        base_ecf=17.5, base_icf=14.6, base_weight=67.0, base_pha=2.8,
        max_day=13,
        ecf_trend="rising",
        ecf_slope=0.065,  # ~+4.3% by day 7 -> matches spec
    ),
    504: dict(
        base_ecf=16.5, base_icf=16.5, base_weight=78.0, base_pha=3.8,
        max_day=40,
        ecf_trend="rising",
        ecf_slope=0.13,  # +5.7% by day 7
    ),
    918: dict(
        base_ecf=17.8, base_icf=15.8, base_weight=80.0, base_pha=4.5,
        max_day=20,
        ecf_trend="v_shape",
        nadir_day=8, drop_rate=0.04, rebound_rate=0.15,
    ),
    1011: dict(
        base_ecf=17.2, base_icf=16.6, base_weight=84.0, base_pha=3.9,
        max_day=29,
        ecf_trend="v_shape",
        nadir_day=10, drop_rate=0.03, rebound_rate=0.12,
    ),
    1012: dict(
        base_ecf=17.2, base_icf=15.3, base_weight=79.0, base_pha=4.8,
        max_day=30,
        ecf_trend="v_shape",
        nadir_day=10, drop_rate=0.17,  # strong initial drop -10%
        rebound_rate=0.12,             # dramatic reversal +15.4%
    ),
    315: dict(
        base_ecf=17.5, base_icf=15.7, base_weight=85.0, base_pha=5.1,
        max_day=36,
        ecf_trend="declining",
        ecf_slope=-0.07,  # steady decline, looks good
    ),
    2001: dict(
        base_ecf=15.0, base_icf=16.2, base_weight=72.0, base_pha=5.5,
        max_day=60,
        ecf_trend="declining_stable",
        ecf_slope=-0.04,
    ),
    2002: dict(
        base_ecf=15.5, base_icf=14.7, base_weight=68.0, base_pha=4.6,
        max_day=60,
        ecf_trend="declining_stable",
        ecf_slope=-0.06,
    ),
}


def _make_day_grid(max_day, readmission_day, rng):
    """Create a realistic measurement day grid with occasional gaps."""
    days = [0]  # always have discharge day
    for d in range(1, max_day + 1):
        # Higher measurement probability in protocol windows
        if 5 <= d <= 9 or 18 <= d <= 24:
            prob = 0.85
        elif d <= 4:
            prob = 0.60
        else:
            prob = 0.55
        if rng.random() < prob:
            days.append(d)

    # Guarantee at least one measurement in each protocol window (if patient survives to it)
    if max_day >= 5:
        if not any(5 <= d <= 9 for d in days):
            days.append(7)
    if max_day >= 18:
        if not any(18 <= d <= 24 for d in days):
            days.append(21)

    # Remove any days past readmission (patient exits monitoring)
    if readmission_day is not None:
        days = [d for d in days if d <= readmission_day]

    return np.array(sorted(set(days)))


def _ecf_trajectory(days, params, rng):
    """Generate ECF (L) trajectory based on phenotype pattern."""
    base = params["base_ecf"]
    trend = params["ecf_trend"]
    n = len(days)
    noise = rng.normal(0, 0.08, n)

    if trend == "flat_high":
        ecf = base + days * params.get("ecf_slope", 0.03) + noise

    elif trend == "rising":
        slope = params["ecf_slope"]
        ecf = base + days * slope + noise

    elif trend == "v_shape":
        nadir = params["nadir_day"]
        drop_rate = params["drop_rate"]
        rebound_rate = params["rebound_rate"]
        ecf = np.empty(n)
        for i, d in enumerate(days):
            if d <= nadir:
                ecf[i] = base - d * drop_rate + noise[i]
            else:
                nadir_val = base - nadir * drop_rate
                ecf[i] = nadir_val + (d - nadir) * rebound_rate + noise[i]

    elif trend == "declining":
        slope = params["ecf_slope"]
        ecf = base + days * slope + noise

    elif trend == "declining_stable":
        slope = params["ecf_slope"]
        # Exponential decay toward stable value
        ecf = base + slope * days * np.exp(-days / 40.0) + noise

    else:
        ecf = np.full(n, base) + noise

    return ecf


def _generate_patient(pid, rng):
    """Generate full time-series DataFrame for one patient."""
    meta = PATIENT_METADATA[pid]
    p = _PARAMS[pid]

    days = _make_day_grid(p["max_day"], meta["readmission_day"], rng)
    n = len(days)

    # ECF trajectory (the primary driver)
    ecf = _ecf_trajectory(days, p, rng)

    # ICF: relatively stable with slow drift and small noise
    icf_drift = rng.normal(0, 0.005, n).cumsum()
    icf = p["base_icf"] + icf_drift + rng.normal(0, 0.1, n)

    # TBW = ECF + ICF (exact relationship)
    tbw = ecf + icf

    # HF-Dex = ECF / TBW * 100 (derived, maintains consistency)
    hf_dex = ecf / tbw * 100.0

    # Weight: loosely correlated with TBW
    base_weight = p["base_weight"]
    tbw_change = tbw - tbw[0]
    weight = base_weight + tbw_change * 0.9 + rng.normal(0, 0.3, n)

    # Phase Angle: patient-specific base with slow drift and noise
    pha_drift = rng.normal(0, 0.01, n).cumsum()
    pha = p["base_pha"] + pha_drift + rng.normal(0, 0.12, n)
    pha = np.clip(pha, 1.5, 8.0)

    df = pd.DataFrame({
        "patient_id": pid,
        "days_from_discharge": days,
        "hf_dex": np.round(hf_dex, 2),
        "ecf_l": np.round(ecf, 2),
        "icf_l": np.round(icf, 2),
        "tbw_l": np.round(tbw, 2),
        "weight_kg": np.round(weight, 1),
        "phase_angle": np.round(pha, 2),
    })
    return df


def _generate_patient_1702(rng):
    """Showcase patient with hand-tuned trajectory matching spec reference.

    HF-Dex bouncing 52-55%, ECF rising from ~17.5 to ~19.5L,
    TBW ~33-36.7L, weight ~67-68.7kg, PhA oscillating 2.4-3.2 deg.
    """
    pid = 1702
    meta = PATIENT_METADATA[pid]

    days = np.array([0, 1, 2, 4, 5, 7, 8, 9, 10, 11, 13])

    # Hand-crafted ECF trajectory: steady rise from 17.5 to ~19.5
    ecf_base = np.array([
        17.50, 17.55, 17.70, 17.85, 18.00, 18.25, 18.40, 18.55, 18.80, 19.00, 19.50
    ])
    ecf = ecf_base + rng.normal(0, 0.05, len(days))

    # ICF: relatively stable ~14.6L
    icf = 14.60 + rng.normal(0, 0.08, len(days))

    tbw = ecf + icf
    hf_dex = ecf / tbw * 100.0

    # Weight tracks TBW
    weight_base = 67.0
    tbw_change = tbw - tbw[0]
    weight = weight_base + tbw_change * 0.8 + rng.normal(0, 0.2, len(days))

    # Phase angle oscillating 2.4-3.2
    pha = np.array([2.80, 2.91, 2.65, 2.78, 3.05, 2.55, 2.90, 3.10, 2.70, 2.45, 3.15])
    pha += rng.normal(0, 0.05, len(days))
    pha = np.clip(pha, 2.0, 4.0)

    df = pd.DataFrame({
        "patient_id": pid,
        "days_from_discharge": days,
        "hf_dex": np.round(hf_dex, 2),
        "ecf_l": np.round(ecf, 2),
        "icf_l": np.round(icf, 2),
        "tbw_l": np.round(tbw, 2),
        "weight_kg": np.round(weight, 1),
        "phase_angle": np.round(pha, 2),
    })
    return df


def get_all_patients():
    """Return combined DataFrame of all 11 demo patients.

    Uses a fixed random seed for reproducibility.
    """
    rng = np.random.default_rng(42)
    frames = []
    for pid in PATIENT_METADATA:
        if pid == 1702:
            frames.append(_generate_patient_1702(rng))
        else:
            frames.append(_generate_patient(pid, rng))

    return pd.concat(frames, ignore_index=True)
