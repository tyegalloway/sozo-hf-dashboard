"""Dashboard header: clean white card with blue accents, patient title, and phenotype badge."""

import streamlit as st


def render_header(patient_id, classification_result):
    """Render a clean white header card with patient info and inline phenotype badge."""
    label = classification_result["label"]
    icon = classification_result["icon"]
    color = classification_result["color"]
    severity = classification_result["severity"]

    # Severity sub-badge (only if present)
    severity_html = ""
    if severity:
        sev_bg = "#FEE2E2" if severity == "ENHANCED MONITORING" else "#FFF7ED"
        sev_color = "#991B1B" if severity == "ENHANCED MONITORING" else "#9A3412"
        severity_html = (
            f'<span style="background: {sev_bg}; color: {sev_color}; padding: 2px 10px; '
            f'border-radius: 10px; font-size: 11px; font-weight: 600; margin-left: 8px; '
            f'vertical-align: middle;">{severity}</span>'
        )

    # Badge colours - softer pastel versions
    badge_bg_map = {
        "#DC2626": "#FEE2E2",  # red -> light red bg
        "#F97316": "#FFF7ED",  # orange -> light orange bg
        "#16A34A": "#DCFCE7",  # green -> light green bg
        "#7C3AED": "#F3E8FF",  # purple -> light purple bg
    }
    badge_text_map = {
        "#DC2626": "#991B1B",
        "#F97316": "#9A3412",
        "#16A34A": "#166534",
        "#7C3AED": "#6B21A8",
    }
    badge_bg = badge_bg_map.get(color, "#EFF6FF")
    badge_text = badge_text_map.get(color, "#1E40AF")

    st.markdown(
        f"""
        <div style="
            background: white;
            padding: 20px 28px;
            border-radius: 12px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        ">
            <div>
                <div style="color: #0066B3; font-size: 12px; font-weight: 600;
                            letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px;">
                    SOZO Pro &bull; HF Protocol Dashboard
                </div>
                <div style="color: #1F2937; font-size: 22px; font-weight: 700;">
                    Patient {patient_id}: Fluid Status &mdash; First 60 Days
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span style="
                    background: {badge_bg};
                    color: {badge_text};
                    padding: 6px 18px;
                    border-radius: 20px;
                    font-weight: 600;
                    font-size: 14px;
                    white-space: nowrap;
                    border: 1px solid {color}22;
                ">{icon} {label}</span>
                {severity_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
