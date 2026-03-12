"""Five-panel Plotly time-series chart for patient fluid status (v2: clean white/grey aesthetic)."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.thresholds import COLORS, DAY7_WINDOW, DAY21_WINDOW

# Very subtle blue-tinted window shading
_DAY7_FILL = "rgba(0, 102, 179, 0.04)"
_DAY21_FILL = "rgba(124, 58, 237, 0.04)"


def _add_shared_elements(fig, readmission_day, num_rows):
    """Add Day 7/21 windows and readmission line to all subplot rows."""
    for row in range(1, num_rows + 1):
        fig.add_vrect(
            x0=DAY7_WINDOW[0], x1=DAY7_WINDOW[1],
            fillcolor=_DAY7_FILL,
            layer="below", line_width=0,
            row=row, col=1,
        )
        fig.add_vrect(
            x0=DAY21_WINDOW[0], x1=DAY21_WINDOW[1],
            fillcolor=_DAY21_FILL,
            layer="below", line_width=0,
            row=row, col=1,
        )
        if readmission_day is not None:
            fig.add_vline(
                x=readmission_day,
                line_dash="dash",
                line_color="#E5E7EB",
                line_width=1.5,
                row=row, col=1,
            )


def _find_readmission_point(df, readmission_day, value_col):
    """Find the data point closest to (but not exceeding) readmission day."""
    if readmission_day is None:
        return None, None
    eligible = df[df["days_from_discharge"] <= readmission_day]
    if eligible.empty:
        return None, None
    closest_idx = (eligible["days_from_discharge"] - readmission_day).abs().idxmin()
    row = eligible.loc[closest_idx]
    return int(row["days_from_discharge"]), float(row[value_col])


def _find_checkpoint_value(df, window, value_col):
    """Find the measurement closest to window centre."""
    mask = (df["days_from_discharge"] >= window[0]) & (df["days_from_discharge"] <= window[1])
    sub = df[mask]
    if sub.empty:
        return None, None
    centre = (window[0] + window[1]) / 2
    idx = (sub["days_from_discharge"] - centre).abs().idxmin()
    row = sub.loc[idx]
    return int(row["days_from_discharge"]), float(row[value_col])


def _add_readmission_marker(fig, df, readmission_day, value_col, fmt, row):
    """Add readmission-day data point marker."""
    rd_x, rd_y = _find_readmission_point(df, readmission_day, value_col)
    if rd_x is not None:
        fig.add_trace(
            go.Scatter(
                x=[rd_x], y=[rd_y],
                mode="markers",
                marker=dict(size=12, color="#DC2626",
                            symbol="circle", line=dict(width=2, color="white")),
                showlegend=False,
                hovertemplate=f"Readmission Day {rd_x}: {rd_y:{fmt}}<extra></extra>",
            ),
            row=row, col=1,
        )


def create_patient_chart(df, patient_id, readmission_day, thresholds):
    """Create the 5-panel stacked figure for one patient (v2 clean style)."""
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        row_heights=[0.24, 0.19, 0.19, 0.19, 0.19],
    )

    days = df["days_from_discharge"]

    # Muted colour palette
    blue = "#0066B3"
    teal = "#0891B2"
    slate = "#64748B"
    emerald = "#059669"
    indigo = "#6366F1"

    # ---- Panel 1: HF-Dex ----
    fig.add_trace(
        go.Scatter(
            x=days, y=df["hf_dex"],
            mode="lines+markers",
            name="HF-Dex",
            line=dict(color=blue, width=2.5),
            marker=dict(size=6, color="white", line=dict(width=2, color=blue)),
            hovertemplate="Day %{x}: %{y:.1f}%<extra>HF-Dex</extra>",
        ),
        row=1, col=1,
    )
    # Threshold line
    fig.add_hline(
        y=thresholds["hf_dex_high_risk"],
        line_dash="dot",
        line_color="#E5E7EB",
        line_width=1.5,
        row=1, col=1,
    )
    fig.add_annotation(
        x=0, y=thresholds["hf_dex_high_risk"],
        text=f"  High Risk ({thresholds['hf_dex_high_risk']:.0f}%)",
        showarrow=False,
        font=dict(size=10, color="#9CA3AF"),
        xanchor="left", yanchor="bottom",
        row=1, col=1,
    )

    # Data labels on key points
    discharge_row = df[df["days_from_discharge"] == 0]
    if not discharge_row.empty:
        val = float(discharge_row["hf_dex"].iloc[0])
        fig.add_annotation(
            x=0, y=val,
            text=f"<b>{val:.1f}%</b>",
            showarrow=True, arrowhead=0, arrowcolor="rgba(0,0,0,0.15)",
            ax=0, ay=-25,
            font=dict(size=10, color=blue),
            bgcolor="rgba(255,255,255,0.9)", borderpad=2,
            row=1, col=1,
        )
    d7_x, d7_y = _find_checkpoint_value(df, DAY7_WINDOW, "hf_dex")
    if d7_x is not None:
        fig.add_annotation(
            x=d7_x, y=d7_y,
            text=f"<b>D7: {d7_y:.1f}%</b>",
            showarrow=True, arrowhead=0, arrowcolor="rgba(0,0,0,0.15)",
            ax=0, ay=-25,
            font=dict(size=10, color=blue),
            bgcolor="rgba(255,255,255,0.9)", borderpad=2,
            row=1, col=1,
        )
    d21_x, d21_y = _find_checkpoint_value(df, DAY21_WINDOW, "hf_dex")
    if d21_x is not None:
        fig.add_annotation(
            x=d21_x, y=d21_y,
            text=f"<b>D21: {d21_y:.1f}%</b>",
            showarrow=True, arrowhead=0, arrowcolor="rgba(0,0,0,0.15)",
            ax=0, ay=-25,
            font=dict(size=10, color=blue),
            bgcolor="rgba(255,255,255,0.9)", borderpad=2,
            row=1, col=1,
        )

    # Readmission annotation
    if readmission_day is not None:
        fig.add_annotation(
            x=readmission_day,
            y=df["hf_dex"].max() + 1.5,
            text=f"<b>READMISSION</b><br>Day {readmission_day}",
            showarrow=True, arrowhead=2,
            bgcolor="#FEE2E2",
            font=dict(color="#991B1B", size=10),
            bordercolor="#FECACA", borderwidth=1, borderpad=5,
            row=1, col=1,
        )
    _add_readmission_marker(fig, df, readmission_day, "hf_dex", ".1f", 1)

    # ---- Panel 2: ECF / ICF ----
    fig.add_trace(
        go.Scatter(
            x=days, y=df["ecf_l"],
            mode="lines+markers", name="ECF",
            line=dict(color=blue, width=2),
            marker=dict(size=4, symbol="circle", color=blue),
            hovertemplate="Day %{x}: %{y:.2f} L<extra>ECF</extra>",
        ),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=days, y=df["icf_l"],
            mode="lines+markers", name="ICF",
            line=dict(color=teal, width=2),
            marker=dict(size=4, symbol="square", color=teal),
            hovertemplate="Day %{x}: %{y:.2f} L<extra>ICF</extra>",
        ),
        row=2, col=1,
    )
    _add_readmission_marker(fig, df, readmission_day, "ecf_l", ".2f", 2)

    # ---- Panel 3: TBW ----
    fig.add_trace(
        go.Scatter(
            x=days, y=df["tbw_l"],
            mode="lines+markers", name="TBW",
            line=dict(color=emerald, width=2),
            marker=dict(size=4, symbol="triangle-up", color=emerald),
            hovertemplate="Day %{x}: %{y:.2f} L<extra>TBW</extra>",
        ),
        row=3, col=1,
    )
    _add_readmission_marker(fig, df, readmission_day, "tbw_l", ".2f", 3)

    # ---- Panel 4: Weight ----
    fig.add_trace(
        go.Scatter(
            x=days, y=df["weight_kg"],
            mode="lines+markers", name="Weight",
            line=dict(color=slate, width=2),
            marker=dict(size=4, symbol="circle", color=slate),
            hovertemplate="Day %{x}: %{y:.1f} kg<extra>Weight</extra>",
        ),
        row=4, col=1,
    )
    _add_readmission_marker(fig, df, readmission_day, "weight_kg", ".1f", 4)

    # ---- Panel 5: Phase Angle ----
    fig.add_trace(
        go.Scatter(
            x=days, y=df["phase_angle"],
            mode="lines+markers", name="Phase Angle",
            line=dict(color=indigo, width=2),
            marker=dict(size=4, symbol="diamond", color=indigo),
            hovertemplate="Day %{x}: %{y:.2f} deg<extra>Phase Angle</extra>",
        ),
        row=5, col=1,
    )
    fig.add_hline(
        y=thresholds["phase_angle_low"],
        line_dash="dot", line_color="#E5E7EB", line_width=1,
        row=5, col=1,
    )
    fig.add_annotation(
        x=0, y=thresholds["phase_angle_low"],
        text=f"  {thresholds['phase_angle_low']:.1f} deg",
        showarrow=False,
        font=dict(size=10, color="#9CA3AF"),
        xanchor="left", yanchor="bottom",
        row=5, col=1,
    )
    _add_readmission_marker(fig, df, readmission_day, "phase_angle", ".2f", 5)

    # ---- Shared elements ----
    _add_shared_elements(fig, readmission_day, 5)

    # ---- Layout ----
    fig.update_layout(
        template="plotly_white",
        height=1150,
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#6B7280"),
        hovermode="x unified",
        margin=dict(l=70, r=30, t=20, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E5E7EB", borderwidth=1,
            font=dict(size=11, color="#6B7280"),
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    # Y-axis labels + gridlines
    y_titles = ["HF-Dex (%)", "Volume (L)", "TBW (L)", "Weight (kg)", "Phase Angle (deg)"]
    for row, title in enumerate(y_titles, start=1):
        fig.update_yaxes(
            title_text=title, row=row, col=1,
            gridcolor="#F3F4F6", gridwidth=1,
            title_font=dict(size=11, color="#9CA3AF"),
            tickfont=dict(color="#9CA3AF"),
        )

    # X-axis
    for row in range(1, 5):
        fig.update_xaxes(showticklabels=False, gridcolor="#F3F4F6", gridwidth=1, row=row, col=1)
    fig.update_xaxes(
        title_text="Days from Discharge",
        range=[-1, 62], dtick=5,
        gridcolor="#F3F4F6", gridwidth=1,
        title_font=dict(color="#9CA3AF"),
        tickfont=dict(color="#9CA3AF"),
        row=5, col=1,
    )

    return fig
