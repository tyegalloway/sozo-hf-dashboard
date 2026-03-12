"""Protocol checkpoint summary card with clean white/grey aesthetic and soft pill badges."""

import streamlit as st


def _badge(text, flagged):
    """Return a soft-coloured HTML pill badge for a flag status."""
    if flagged:
        return (
            f'<span style="background: #FEE2E2; color: #991B1B; padding: 3px 12px; '
            f'border-radius: 10px; font-size: 11px; font-weight: 700; white-space: nowrap;">'
            f'{text}</span>'
        )
    return (
        f'<span style="background: #DCFCE7; color: #166534; padding: 3px 12px; '
        f'border-radius: 10px; font-size: 11px; font-weight: 700; white-space: nowrap;">'
        f'{text}</span>'
    )


def render_summary_card(classification_result, readmission_day):
    """Render the protocol checkpoint summary as a clean white table card."""
    cp = classification_result["checkpoints"]
    flags = classification_result["flags"]
    flag_count = classification_result["flag_count"]
    total_flags = classification_result["total_flags"]

    # --- Build table rows ---
    rows = []

    # Discharge
    hf_dex = cp["discharge"]["hf_dex"]
    badge = _badge("HIGH RISK", True) if flags["discharge_high_risk"] else _badge("STANDARD", False)
    rows.append(
        f'<tr>'
        f'<td style="font-weight:600; padding:10px 16px; white-space:nowrap; color:#374151;">DISCHARGE</td>'
        f'<td style="padding:10px 16px; color:#4B5563;">HF-Dex = <strong>{hf_dex:.1f}%</strong></td>'
        f'<td style="padding:10px 16px; text-align:right;">{badge}</td>'
        f'</tr>'
    )

    # Day 7
    d7 = cp["day7"]
    if d7["found"]:
        hf7 = f"{d7['hf_dex']:.1f}%" if d7["hf_dex"] is not None else "N/A"
        delta = f"{d7['delta_ecf_pct']:+.1f}%" if d7["delta_ecf_pct"] is not None else "N/A"
        if flags["day7_not_decongesting"]:
            badge = _badge("FLAG - Not Decongesting", True)
        else:
            badge = _badge("Decongesting", False)
        detail = f"HF-Dex = <strong>{hf7}</strong> &nbsp;|&nbsp; ECF &Delta; = <strong>{delta}</strong>"
    else:
        badge = '<span style="color:#9CA3AF; font-size:12px; font-style:italic;">No measurement in window</span>'
        detail = "N/A"
    rows.append(
        f'<tr style="background: #F9FAFB;">'
        f'<td style="font-weight:600; padding:10px 16px; white-space:nowrap; color:#374151;">DAY 7</td>'
        f'<td style="padding:10px 16px; color:#4B5563;">{detail}</td>'
        f'<td style="padding:10px 16px; text-align:right;">{badge}</td>'
        f'</tr>'
    )

    # Day 21
    d21 = cp["day21"]
    if d21["found"]:
        delta21 = f"{d21['delta_ecf_pct']:+.1f}%" if d21["delta_ecf_pct"] is not None else "N/A"
        if flags["day21_recongestion"]:
            badge = _badge("RECONGESTION", True)
        else:
            badge = _badge("Stable", False)
        detail = f"ECF &Delta;<sub>7-21</sub> = <strong>{delta21}</strong>"
    else:
        badge = '<span style="color:#9CA3AF; font-size:12px; font-style:italic;">No measurement in window</span>'
        detail = "N/A"
    rows.append(
        f'<tr>'
        f'<td style="font-weight:600; padding:10px 16px; white-space:nowrap; color:#374151;">DAY 21</td>'
        f'<td style="padding:10px 16px; color:#4B5563;">{detail}</td>'
        f'<td style="padding:10px 16px; text-align:right;">{badge}</td>'
        f'</tr>'
    )

    # Phase Angle
    pha = cp["phase_angle"]
    if pha["low"]:
        badge = _badge("LOW (<3.5 deg)", True)
    else:
        badge = _badge("Adequate", False)
    rows.append(
        f'<tr style="background: #F9FAFB;">'
        f'<td style="font-weight:600; padding:10px 16px; white-space:nowrap; color:#374151;">PHASE ANGLE</td>'
        f'<td style="padding:10px 16px; color:#4B5563;">Discharge PhA = <strong>{pha["value"]:.1f} deg</strong></td>'
        f'<td style="padding:10px 16px; text-align:right;">{badge}</td>'
        f'</tr>'
    )

    # --- Readmission footer ---
    if readmission_day is not None:
        footer_bg = "#FEF2F2"
        footer_border = "#FECACA"
        footer_text = (
            f'<span style="color:#991B1B; font-weight:700;">READMISSION: Day {readmission_day}</span>'
            f'&nbsp;&nbsp;&bull;&nbsp;&nbsp;'
            f'<span style="color:#991B1B;">Protocol Flags Triggered: '
            f'<strong>{flag_count}/{total_flags}</strong></span>'
        )
    else:
        footer_bg = "#F0FDF4"
        footer_border = "#BBF7D0"
        footer_text = (
            '<span style="color:#166534; font-weight:700;">'
            'No readmission in 60-day window</span>'
        )

    # --- Assemble card ---
    card_html = f"""
    <div style="
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 20px;
        color: #1F2937;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 13px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    ">
        <div style="
            background: #F9FAFB;
            padding: 12px 16px;
            font-weight: 700;
            font-size: 13px;
            color: #6B7280;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            border-bottom: 1px solid #E5E7EB;
        ">Protocol Checkpoint Summary</div>
        <table style="width:100%; border-collapse:collapse;">
            {''.join(rows)}
        </table>
        <div style="
            background: {footer_bg};
            border-top: 1px solid {footer_border};
            padding: 12px 16px;
            font-family: monospace;
            font-size: 13px;
        ">{footer_text}</div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)
