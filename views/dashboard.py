from __future__ import annotations

import json
from datetime import datetime
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.db import HIGH_RISK_LABELS, LOW_RISK_LABELS, display_id, fetch_all_patients, get_assessment_history, load_patient_record
from utils.ui import render_status_chip


COLOR_GOOD = "#256C4C"
COLOR_ATTENTION = "#A63838"
COLOR_MONITOR = "#8A5A00"
COLOR_MUTED = "#7B8790"
GRIDLINE = "#D9DED9"
AXIS_INK = "#102A43"


def _format_date(value: object, *, fallback: str = "Not recorded") -> str:
    raw = str(value or "").strip()
    if not raw:
        return fallback
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%b %d, %Y").replace(" 0", " ")
    except ValueError:
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").strftime("%b %d, %Y").replace(" 0", " ")
        except ValueError:
            return raw


def _status_for(label: object) -> tuple[str, str]:
    if str(label or "") in HIGH_RISK_LABELS:
        return "Needs review", "needs-review"
    if not label or str(label) == "Pending":
        return "Monitor", "monitor"
    return "Stable", "stable"


def _worklist_row(row: pd.Series) -> dict:
    patient_id = int(row["id"])
    history = get_assessment_history(patient_id)
    latest_assessment = "Not assessed"
    risk_change = "No prior comparison"
    if not history.empty:
        latest = history.iloc[-1]
        latest_assessment = _format_date(latest.get("recorded_at"))
        risk_values = pd.to_numeric(history.get("risk_percent"), errors="coerce").dropna()
        if len(risk_values) >= 2:
            delta = float(risk_values.iloc[-1] - risk_values.iloc[-2])
            risk_change = f"{delta:+.1f} pts"
        elif len(risk_values) == 1:
            risk_change = "Baseline"

    last_contact = "Not recorded"
    try:
        record = json.loads(row.get("extended_record") or "{}")
        contact_dates = [
            str(item.get("date") or "")
            for item in (record.get("visits") or [])
            if item.get("date")
        ]
        if contact_dates:
            last_contact = _format_date(max(contact_dates))
    except (TypeError, json.JSONDecodeError):
        pass

    status, tone = _status_for(row.get("prediction_label"))
    return {
        "id": patient_id,
        "Patient": f"{display_id(patient_id)} · {row.get('full_name') or 'Unnamed patient'}",
        "Status": status,
        "tone": tone,
        "Latest assessment": latest_assessment,
        "Risk change": risk_change,
        "Last contact": last_contact,
        "Last updated": _format_date(row.get("last_modified_at"), fallback=_format_date(row.get("registration_date"))),
        "label": str(row.get("prediction_label") or "Pending"),
        "confidence": row.get("confidence"),
        "age": row.get("age"),
        "gender": row.get("gender"),
    }


def _bar_figure(categories: list[str], values: list[int], colors: list[str]) -> go.Figure:
    fig = go.Figure(go.Bar(x=categories, y=values, marker_color=colors, marker_line_width=0))
    fig.update_layout(
        height=250,
        margin=dict(l=8, r=8, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor=GRIDLINE, tickfont=dict(color=AXIS_INK, size=12), title="Patients"),
        xaxis=dict(tickfont=dict(color=AXIS_INK, size=12)),
        font=dict(color=AXIS_INK),
        showlegend=False,
    )
    return fig


df = fetch_all_patients()
if df.empty:
    rows = []
else:
    with st.spinner("Loading patient worklist…"):
        rows = [_worklist_row(row) for _, row in df.iterrows()]
priority = {"Needs review": 0, "Monitor": 1, "Stable": 2}
rows.sort(key=lambda item: (priority[item["Status"]], item["Last updated"]), reverse=False)

needs_review = sum(item["Status"] == "Needs review" for item in rows)
monitor = sum(item["Status"] == "Monitor" for item in rows)
stable = sum(item["Status"] == "Stable" for item in rows)

st.markdown(
    """
    <style>
    .dashboard-lede { display:flex; justify-content:space-between; gap:16px; align-items:flex-end; margin-bottom:18px; }
    .dashboard-lede p { color:var(--ink-secondary); margin:6px 0 0; font-size:16px; }
    .dashboard-updated { color:var(--ink-muted); font-size:13px; text-align:right; }
    .st-key-worklist_card { padding:4px; }
    .worklist-caption { color:var(--ink-secondary); margin-top:-3px; font-size:14px; }
    .details-name { margin:0 0 3px; color:var(--brand-navy); }
    .details-meta { color:var(--ink-secondary); font-size:14px; }
    @media (max-width:768px) { .dashboard-lede { display:block; } .dashboard-updated { text-align:left; margin-top:10px; } }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='dashboard-lede'><div><div class='bg-title'>Clinical dashboard</div>"
    "<p>Prioritize follow-up with a concise view of current assessments and chart activity.</p></div>"
    f"<div class='dashboard-updated'>Last updated<br><strong>{datetime.now().strftime('%b %d, %Y · %I:%M %p')}</strong></div></div>",
    unsafe_allow_html=True,
)

metric_cols = st.columns(4, gap="medium")
for col, label, value, detail in (
    (metric_cols[0], "Total patients", len(rows), "All active records"),
    (metric_cols[1], "Needs review", needs_review, "Assessment needs follow-up"),
    (metric_cols[2], "Monitor", monitor, "No completed assessment yet"),
    (metric_cols[3], "Stable", stable, "Lower-priority review"),
):
    with col:
        st.metric(label, value, help=detail)

st.markdown("<div class='bg-section'>Patient worklist</div>", unsafe_allow_html=True)
filter_col, status_col = st.columns([2.3, 1], gap="medium")
with filter_col:
    query = st.text_input("Search patients", placeholder="Search by patient name or ID", key="dashboard_search")
with status_col:
    status_filter = st.selectbox("Status", ["All statuses", "Needs review", "Monitor", "Stable"], key="dashboard_status_filter")

filtered = rows
if query.strip():
    lower_query = query.strip().lower()
    filtered = [item for item in filtered if lower_query in item["Patient"].lower()]
if status_filter != "All statuses":
    filtered = [item for item in filtered if item["Status"] == status_filter]

table_col, detail_col = st.columns([1.65, 0.75], gap="large")
with table_col:
    with st.container(border=True, key="worklist_card"):
        st.markdown("<div class='worklist-caption'>Patients are ordered with follow-up needs first. Every status includes a text label.</div>", unsafe_allow_html=True)
        if not filtered:
            st.info("No patients match these filters.")
        else:
            table = pd.DataFrame(
                [
                    {
                        "Patient": item["Patient"],
                        "Status": item["Status"],
                        "Latest assessment": item["Latest assessment"],
                        "Risk change": item["Risk change"],
                        "Last contact": item["Last contact"],
                        "Last updated": item["Last updated"],
                    }
                    for item in filtered
                ]
            )
            st.dataframe(table, width="stretch", hide_index=True, height=min(520, 92 + len(table) * 36))

with detail_col:
    with st.container(border=True, key="patient_side_panel"):
        st.markdown("<div class='role-card-kicker'>Patient details</div>", unsafe_allow_html=True)
        if not filtered:
            st.caption("Choose a different filter to inspect a patient.")
        else:
            options = {item["Patient"]: item for item in filtered}
            selected_label = st.selectbox("Select a patient", list(options), key="dashboard_patient_select")
            selected = options[selected_label]
            st.markdown(f"<h3 class='details-name'>{escape(selected['Patient'])}</h3>", unsafe_allow_html=True)
            render_status_chip(selected["Status"], tone=selected["tone"])
            st.markdown(
                f"<p class='details-meta'>Model result: <strong>{escape(selected['label'])}</strong><br>"
                f"Latest assessment: <strong>{escape(selected['Latest assessment'])}</strong><br>"
                f"Risk change: <strong>{escape(selected['Risk change'])}</strong><br>"
                f"Last contact: <strong>{escape(selected['Last contact'])}</strong></p>",
                unsafe_allow_html=True,
            )
            if st.button("Open patient record", icon=":material/open_in_new:", type="primary", width="stretch", key="dashboard_open_patient"):
                patient_id = int(selected["id"])
                st.session_state.selected_patient_id = patient_id
                st.session_state.selected_patient = selected["Patient"]
                st.session_state.patient_record = load_patient_record(patient_id)
                st.session_state.patient_record_id = patient_id
                st.switch_page("views/patient_detail.py")

with st.expander("Population trends", expanded=False):
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Current review status")
        st.plotly_chart(
            _bar_figure(["Needs review", "Monitor", "Stable"], [needs_review, monitor, stable], [COLOR_ATTENTION, COLOR_MONITOR, COLOR_GOOD]),
            width="stretch",
            theme=None,
        )
    with right:
        st.subheader("Age distribution")
        if df.empty:
            st.info("No patient data is available yet.")
        else:
            bins = ["0–49", "50–59", "60–69", "70–79", "80+"]
            ages = pd.cut(df["age"], bins=[0, 49, 59, 69, 79, 120], labels=bins).value_counts().reindex(bins, fill_value=0)
            st.plotly_chart(_bar_figure(bins, list(ages.values), ["#BFD8D0", "#91BDB2", "#5A9C91", "#3F7C74", "#276D68"]), width="stretch", theme=None)

st.warning(
    "BrainGuard AI is a clinical decision-support prototype. Assessment labels are not diagnoses and should always be reviewed alongside clinical judgment."
)
