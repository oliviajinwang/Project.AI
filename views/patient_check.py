import streamlit as st

from utils.gauge import render_risk_gauge
from utils.report import RECOMMENDATIONS
from utils.shap_chart import render_shap_breakdown
from src.predict_lifestyle import predict_lifestyle

st.markdown("<div class='bg-section'>Dementia Risk Check</div>", unsafe_allow_html=True)
st.write("Answer a few questions about your lifestyle to see your estimated dementia risk.")
st.caption("AI-assisted estimate based on lifestyle and health history — not a diagnosis.")

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
    patient = {
        "age": age,
        "gender_male": int(gender == "Male"),
        "education_years": education_years,
        "diabetes": int(diabetes),
        "hypertension": int(hypertension),
        "high_cholesterol": int(high_cholesterol),
        "smoking": int(smoking),
    }
    st.session_state["patient_result"] = predict_lifestyle(patient)

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

    if result["label"] == "High Risk":
        st.warning(
            "**What this means:** this screening flagged a higher likelihood of "
            "modifiable dementia risk factors based on the answers entered. It is "
            "**not a diagnosis** — many people who score High Risk here never go on "
            "to develop dementia, and this tool has no access to MRI scans or "
            "cognitive test results, which a real evaluation would use.\n\n"
            "**Suggested next step:** share this result with the person's primary "
            "care physician. They can order a proper cognitive assessment (such as "
            "an MMSE) if it seems warranted."
        )
    else:
        st.success(
            "**What this means:** based on the factors entered, this screening did "
            "not flag elevated risk. This isn't a guarantee — regular checkups "
            "remain the best way to catch changes early, especially as risk factors "
            "like age change over time."
        )

    st.caption(
        "This estimate comes from a machine-learning model trained on a limited "
        "research dataset (not a large clinical trial). Individual results can "
        "vary, and this tool cannot replace a qualified physician's judgment."
    )

    st.markdown("---")
    st.subheader("Why did the model make this prediction?")
    st.plotly_chart(
        render_shap_breakdown(result["importance"], top_n=5),
        width="stretch",
        theme=None,
    )
    for _, row in result["importance"].head(5).iterrows():
        direction = "Increased risk" if row["impact"] > 0 else "Reduced risk"
        st.write(f"**{row['feature']}** — {direction}\n\n{row['text']}")
