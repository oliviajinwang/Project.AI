import plotly.graph_objects as go


def render_risk_gauge(risk_percent: float, subtitle: str) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_percent,
            number={"suffix": "%"},
            title={"text": subtitle},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#4B3F72"},
                "steps": [
                    {"range": [0, 30], "color": "#e5f6e5"},
                    {"range": [30, 60], "color": "#fff4e0"},
                    {"range": [60, 100], "color": "#fbe4e4"},
                ],
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig
