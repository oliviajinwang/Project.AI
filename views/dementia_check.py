import streamlit as st

from utils.db import display_id, fetch_all_patients, update_assessment
from utils.gauge import render_risk_gauge
from utils.mock_predict import get_mock_prediction
from utils.report import RECOMMENDATIONS

COLOR_GOOD = "#0ca30c"
COLOR_WARNING = "#fab219"
COLOR_CRITICAL = "#d03b3b"
CLASS_COLORS = {"Nondemented": COLOR_GOOD, "Converted": COLOR_WARNING, "Demented": COLOR_CRITICAL}

st.markdown("<div class='bg-section'>🧠 Dementia Check</div>", unsafe_allow_html=True)
st.write("Run an AI-assisted dementia risk assessment using lifestyle or clinical data.")
st.caption("Predictions shown here are placeholder values until the trained model is connected.")

patients_df = fetch_all_patients()
patient_options = {"— Quick assessment (not saved) —": None}
for _, row in patients_df.iterrows():
    patient_options[f"{display_id(row['id'])} - {row['full_name']}"] = int(row["id"])

selected_label = st.selectbox("Patient", list(patient_options.keys()))
selected_patient_id = patient_options[selected_label]


tab_lifestyle, tab_clinical = st.tabs(["🧑 Lifestyle Assessment", "🩺 Clinical Assessment"])

with tab_lifestyle:
    st.caption("Layperson-friendly fields — no MRI or imaging data required.")
    col1, col2 = st.columns(2)
    with col1:
        ls_age = st.slider("Age", 40, 90, 60, key="ls_age")
        ls_gender = st.selectbox("Gender", ["Female", "Male"], key="ls_gender")
        ls_education = st.slider("Years of Education", 0, 25, 12, key="ls_edu")
    with col2:
        ls_diabetes = st.toggle("Diabetes Mellitus", key="ls_diabetes")
        ls_hypertension = st.toggle("Hypertension", key="ls_hyper")
        ls_cholesterol = st.toggle("High Cholesterol", key="ls_chol")
        ls_smoking = st.toggle("Smoking", key="ls_smoke")

    if st.button("Run Lifestyle Assessment", type="primary", key="run_lifestyle"):
        label, confidence = get_mock_prediction("lifestyle")
        st.session_state["lifestyle_result"] = {
            "label": label,
            "confidence": confidence,
            "fields": {
                "education_years": ls_education,
                "diabetes": int(ls_diabetes),
                "hypertension": int(ls_hypertension),
                "high_cholesterol": int(ls_cholesterol),
                "smoking": int(ls_smoking),
            },
        }

    if "lifestyle_result" in st.session_state:
        result = st.session_state["lifestyle_result"]
        risk_percent = result["confidence"] if result["label"] == "High Risk" else 100 - result["confidence"]
        st.plotly_chart(
            render_risk_gauge(risk_percent, "Estimated dementia risk"),
            width="stretch",
            theme=None,
        )
        st.caption(f"Model prediction: **{result['label']}** ({result['confidence']:.1f}% confidence)")
        st.info(RECOMMENDATIONS.get(result["label"], ""))
        if selected_patient_id is not None:
            if st.button("💾 Save to Patient Record", key="save_lifestyle"):
                update_assessment(selected_patient_id, "Lifestyle", result["fields"], result["label"], result["confidence"])
                st.success("Saved to patient record.")
        else:
            st.caption("Select a registered patient above to save this result.")

with tab_clinical:
    st.caption("Advanced diagnostic fields — cognitive scores and structural neuroimaging.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Cognitive & Microvascular**")
        cl_ef = st.number_input("EF (Executive Function Z-score)", -3.0, 3.0, 0.0, key="cl_ef")
        cl_ps = st.number_input("PS (Processing Speed Z-score)", -3.0, 3.0, 0.0, key="cl_ps")
        cl_gc = st.number_input("Global Cognitive Score", -3.0, 3.0, 0.0, key="cl_gc")
        cl_fazekas = st.selectbox("Fazekas Score", [0, 1, 2, 3], key="cl_fazekas")
        cl_lacune = st.number_input("Lacune Count", 0, 20, 0, key="cl_lacune")
    with col2:
        st.markdown("**Structural Neuroimaging (OASIS)**")
        cl_mmse = st.slider("MMSE", 0, 30, 27, key="cl_mmse")
        cl_etiv = st.number_input("eTIV", 1000.0, 2000.0, 1450.0, key="cl_etiv")
        cl_nwbv = st.number_input("nWBV", 0.5, 0.9, 0.72, key="cl_nwbv")
        cl_asf = st.number_input("ASF", 0.5, 2.0, 1.1, key="cl_asf")

    if st.button("Run Clinical Assessment", type="primary", key="run_clinical"):
        label, confidence = get_mock_prediction("clinical")
        st.session_state["clinical_result"] = {
            "label": label,
            "confidence": confidence,
            "fields": {
                "ef": cl_ef,
                "ps": cl_ps,
                "global_cognitive": cl_gc,
                "fazekas": cl_fazekas,
                "lacune_count": cl_lacune,
                "mmse": cl_mmse,
                "etiv": cl_etiv,
                "nwbv": cl_nwbv,
                "asf": cl_asf,
            },
        }

    if "clinical_result" in st.session_state:
        result = st.session_state["clinical_result"]
        badge_color = CLASS_COLORS.get(result["label"], "#898781")
        st.markdown(
            f"<div style='padding:14px 18px;border-radius:10px;background:{badge_color}1a;"
            f"border-left:5px solid {badge_color};'>"
            f"<span style='color:{badge_color};font-size:20px;'>●</span> "
            f"<span style='font-size:20px;font-weight:bold;color:#0b0b0b;'>{result['label']}</span>"
            f"<span style='color:#52514e;'> — Confidence: {result['confidence']:.1f}%</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.info(RECOMMENDATIONS.get(result["label"], ""))
        if selected_patient_id is not None:
            if st.button("💾 Save to Patient Record", key="save_clinical"):
                update_assessment(selected_patient_id, "Clinical", result["fields"], result["label"], result["confidence"])
                st.success("Saved to patient record.")
        else:
            st.caption("Select a registered patient above to save this result.")

st.markdown("---")
st.info("🔬 Risk factor breakdown (SHAP) — coming once the model is trained.")
