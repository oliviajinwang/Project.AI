import streamlit as st

from utils.gauge import render_risk_gauge
from utils.mock_predict import get_mock_prediction
from utils.report import RECOMMENDATIONS

st.markdown("<div class='bg-section'>🧑 Dementia Risk Check</div>", unsafe_allow_html=True)
st.write("Answer a few questions about your lifestyle to see your estimated dementia risk.")
st.caption("Predictions shown here are placeholder values until the trained model is connected.")

col1, col2 = st.columns(2)
with col1:
    age = st.slider("Age", 40, 90, 60)
    gender = st.selectbox("Gender", ["Female", "Male"])
    education_years = st.slider("Years of Education", 0, 25, 12)
with col2:
    diabetes = st.toggle("Diabetes")
    hypertension = st.toggle("Hypertension")
    high_cholesterol = st.toggle("High Cholesterol")
    smoking = st.toggle("Smoking")

if st.button("Check My Risk", type="primary"):
    label, confidence = get_mock_prediction("lifestyle")
    st.session_state["patient_result"] = {"label": label, "confidence": confidence}

if "patient_result" in st.session_state:
    result = st.session_state["patient_result"]
    risk_percent = result["confidence"] if result["label"] == "High Risk" else 100 - result["confidence"]
    st.plotly_chart(
        render_risk_gauge(risk_percent, "Estimated dementia risk"),
        width="stretch",
        theme=None,
    )
    st.caption(f"Model prediction: **{result['label']}** ({result['confidence']:.1f}% confidence)")
    st.info(RECOMMENDATIONS.get(result["label"], ""))

st.markdown("---")
st.info("🔬 Risk factor breakdown (SHAP) — coming once the model is trained.")
