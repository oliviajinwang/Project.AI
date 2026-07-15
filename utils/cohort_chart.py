import pandas as pd
import plotly.graph_objects as go

# Literal mirrors of the CSS theme tokens in utils/layout.py (--good,
# --critical, --moderate, --ink-primary) -- Plotly cannot read CSS variables,
# so keep these in sync. No new palette introduced.
COLOR_MUTED = "#7B8790"
COLOR_HIGH_RISK = "#A63838"
COLOR_LOW_RISK = "#256C4C"
COLOR_WARNING = "#8A5A00"
AXIS_INK = "#102A43"
GRIDLINE = "#D9DED9"

PATIENT_LABEL_COLORS = {
    "Nondemented": COLOR_LOW_RISK,
    "Demented": COLOR_HIGH_RISK,
    "Converted": COLOR_WARNING,
    "Low Risk": COLOR_LOW_RISK,
    "High Risk": COLOR_HIGH_RISK,
}


def render_cohort_scatter(
    cohort_df: pd.DataFrame,
    patient_age: float,
    patient_nwbv: float,
    patient_label: str,
) -> go.Figure:
    """Scatter of the training cohort's Age vs nWBV, with the current
    patient's own point highlighted so a clinician can see where they fall
    relative to the rest of the dataset.
    """
    patient_color = PATIENT_LABEL_COLORS.get(patient_label, COLOR_MUTED)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=cohort_df["age"],
            y=cohort_df["normalized_whole_brain_volume"],
            mode="markers",
            name="Cohort (training data)",
            marker=dict(color=COLOR_MUTED, size=7, opacity=0.55),
            hovertemplate="Age %{x}<br>nWBV %{y:.3f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[patient_age],
            y=[patient_nwbv],
            mode="markers",
            name=f"This patient ({patient_label})",
            marker=dict(
                color=patient_color,
                size=16,
                line=dict(color="white", width=2),
            ),
            hovertemplate=f"This patient<br>Age %{{x}}<br>nWBV %{{y:.3f}}<extra></extra>",
        )
    )

    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=30, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=AXIS_INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(
            title="Age",
            gridcolor=GRIDLINE,
            tickfont=dict(color=AXIS_INK),
            automargin=True,
        ),
        yaxis=dict(
            title="Normalized Whole Brain Volume (nWBV)",
            gridcolor=GRIDLINE,
            tickfont=dict(color=AXIS_INK),
            automargin=True,
        ),
    )

    return fig
