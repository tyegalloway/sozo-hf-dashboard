"""SOZO HF Protocol Dashboard v2 - Clean white/grey aesthetic with ImpediMed blue."""

import streamlit as st

from data.demo_patients import get_all_patients, PATIENT_METADATA
from classification.phenotype_engine import classify_patient
from components.header import render_header
from components.summary_card import render_summary_card
from components.charts import create_patient_chart
from utils.thresholds import (
    DEFAULT_THRESHOLDS,
    PHENOTYPE_INFO,
    PHENOTYPE_EXPLAINERS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SOZO HF Protocol Dashboard",
    page_icon="\U0001F4A7",  # water droplet
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Inject custom CSS for clean white/grey look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Force light backgrounds */
    .stApp {
        background-color: #FAFBFC;
    }
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #374151;
    }

    /* Clean selectbox and slider styling */
    .stSelectbox label, .stSlider label {
        color: #6B7280 !important;
        font-weight: 500 !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        color: #374151 !important;
        font-weight: 600 !important;
    }

    /* Remove default Streamlit padding at top */
    .block-container {
        padding-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Load data (cached)
# ---------------------------------------------------------------------------


@st.cache_data
def load_data():
    return get_all_patients()


all_data = load_data()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="text-align:center; padding: 12px 0 8px 0;">'
        '<span style="color: #0066B3; font-size: 20px; font-weight: 700; '
        'letter-spacing: 0.5px;">SOZO HF Protocol</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Patient selector
    patient_ids = list(PATIENT_METADATA.keys())
    patient_labels = {}
    for pid in patient_ids:
        meta = PATIENT_METADATA[pid]
        p = meta["phenotype"]
        if p:
            info = PHENOTYPE_INFO[p]
            patient_labels[pid] = f"Patient {pid} \u2014 {p}: {info['label']}"
        else:
            patient_labels[pid] = f"Patient {pid} \u2014 No Readmission"

    default_idx = patient_ids.index(1702) if 1702 in patient_ids else 0

    selected_id = st.selectbox(
        "Select Patient",
        options=patient_ids,
        format_func=lambda x: patient_labels[x],
        index=default_idx,
    )

    st.markdown("---")

    # Threshold sliders
    with st.expander("Protocol Thresholds", expanded=False):
        hf_dex_thresh = st.slider(
            "HF-Dex High Risk (%)",
            min_value=48.0, max_value=55.0,
            value=DEFAULT_THRESHOLDS["hf_dex_high_risk"],
            step=0.5,
        )
        day7_ecf_thresh = st.slider(
            "Day 7 ECF Flag (%)",
            min_value=-5.0, max_value=10.0,
            value=DEFAULT_THRESHOLDS["day7_ecf_flag"],
            step=0.5,
        )
        day21_recong_thresh = st.slider(
            "Day 21 Recongestion (%)",
            min_value=0.0, max_value=15.0,
            value=DEFAULT_THRESHOLDS["day21_recongestion"],
            step=0.5,
        )
        pha_thresh = st.slider(
            "Phase Angle Low (deg)",
            min_value=3.0, max_value=6.0,
            value=DEFAULT_THRESHOLDS["phase_angle_low"],
            step=0.1,
        )

    st.markdown("---")

    with st.expander("About This Dashboard"):
        st.markdown(
            "This dashboard visualises post-discharge fluid status in heart failure "
            "patients using SOZO Pro bioimpedance spectroscopy data. Patients are "
            "auto-classified into clinical phenotypes based on the SOZO HF Protocol."
        )
        st.caption(
            "Demo data based on the HF at Home study (n=83). "
            "Individual patient trajectories reflect actual clinical patterns."
        )

# ---------------------------------------------------------------------------
# Build current thresholds from slider values
# ---------------------------------------------------------------------------
thresholds = {
    "hf_dex_high_risk": hf_dex_thresh,
    "day7_ecf_flag": day7_ecf_thresh,
    "day21_recongestion": day21_recong_thresh,
    "phase_angle_low": pha_thresh,
}

# ---------------------------------------------------------------------------
# Filter data and classify
# ---------------------------------------------------------------------------
patient_df = all_data[all_data["patient_id"] == selected_id].copy()
meta = PATIENT_METADATA[selected_id]
result = classify_patient(patient_df, meta, thresholds)

# ---------------------------------------------------------------------------
# Render main content
# ---------------------------------------------------------------------------

# 1. Header
render_header(selected_id, result)

# 2. Summary card
render_summary_card(result, meta["readmission_day"])

# 3. Inline chart legend (clean horizontal strip)
st.markdown(
    """
    <div style="
        display: flex;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
        padding: 8px 16px;
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 12px;
        color: #6B7280;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    ">
        <span>
            <span style="display:inline-block; width:14px; height:14px;
                         background:rgba(0,102,179,0.08); border:1px solid #0066B3;
                         vertical-align:middle; border-radius:2px;"></span>
            &nbsp;Day 7 Window (days 5-9)
        </span>
        <span>
            <span style="display:inline-block; width:14px; height:14px;
                         background:rgba(124,58,237,0.08); border:1px solid #7C3AED;
                         vertical-align:middle; border-radius:2px;"></span>
            &nbsp;Day 21 Window (days 18-24)
        </span>
        <span>
            <span style="display:inline-block; width:16px; height:0;
                         border-top:2px dashed #D1D5DB; vertical-align:middle;"></span>
            &nbsp;Readmission Day
        </span>
        <span>
            <span style="display:inline-block; width:16px; height:0;
                         border-top:2px dotted #D1D5DB; vertical-align:middle;"></span>
            &nbsp;High Risk Threshold
        </span>
        <span>
            <span style="display:inline-block; width:12px; height:12px;
                         background:#DC2626; border-radius:50%; vertical-align:middle;
                         border:2px solid white; box-shadow:0 0 0 1px #DC2626;"></span>
            &nbsp;Readmission-day measurement
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. Chart
fig = create_patient_chart(patient_df, selected_id, meta["readmission_day"], thresholds)
st.plotly_chart(fig, use_container_width=True)

# 5. Phenotype explainer
phenotype_key = result["phenotype"] if result["phenotype"] else "None"
explainer_text = PHENOTYPE_EXPLAINERS.get(phenotype_key, "")
if explainer_text:
    with st.expander("Understanding this Phenotype"):
        st.markdown(explainer_text)
