import json

import joblib
import pandas as pd
import numpy as np
import streamlit as st


@st.cache_resource
def _load_model():
    return joblib.load("models/clinician_model.pkl")


@st.cache_resource
def _load_explainer():
    return joblib.load("models/clinician_shap_explainer.pkl")


@st.cache_resource
def _load_threshold():
    with open("models/clinical_threshold.json") as f:
        return json.load(f)["threshold"]


@st.cache_resource
def _load_metrics():
    # Group-aware cross-validated accuracy/AUC, computed separately from
    # training (see models/clinical_metrics.json) -- classes here are
    # roughly balanced (190 vs 183), so plain accuracy is a fair headline
    # number, unlike the lifestyle model.
    with open("models/clinical_metrics.json") as f:
        return json.load(f)


model = _load_model()
explainer = _load_explainer()
DECISION_THRESHOLD = _load_threshold()
MODEL_METRICS = _load_metrics()


FEATURE_DESCRIPTIONS = {
    "age": "Age",
    "education_years": "Years of Education",
    "mmse_score": "MMSE Cognitive Score",
    "estimated_intracranial_volume": "Brain Intracranial Volume",
    "normalized_whole_brain_volume": "Whole Brain Volume",
    "atlas_scaling_factor": "Atlas Scaling Factor",
    "socioeconomic_status": "Socioeconomic Status",
    "gender_male": "Gender"
}

def explain_feature(feature, value, shap_value):

    name = FEATURE_DESCRIPTIONS.get(feature, feature)

    increased = shap_value > 0
    direction = "increased" if increased else "decreased"

    if feature == "mmse_score":

        if value >= 28:
            text = (
                f"An MMSE score of {value:.0f}/30 indicates relatively preserved "
                "cognitive function, which lowered the model's estimated dementia risk."
            )

        elif value >= 24:
            text = (
                f"An MMSE score of {value:.0f}/30 suggests mild cognitive impairment. "
                "This contributed moderately to the model's prediction."
            )

        else:
            text = (
                f"An MMSE score of {value:.0f}/30 is associated with substantial "
                "cognitive impairment and increased the model's estimated dementia risk."
            )

    elif feature == "age":

        if value >= 80:
            text = (
                f"The patient's age ({int(value)} years) is considerably above the "
                "average in the training data and increased the estimated dementia risk."
            )

        elif value >= 70:
            text = (
                f"The patient's age ({int(value)} years) modestly increased the "
                "estimated dementia risk."
            )

        else:
            text = (
                f"The patient's age ({int(value)} years) had little influence on the "
                "overall prediction."
            )

    elif feature == "normalized_whole_brain_volume":

        if value < 0.70:
            text = (
                f"A lower whole brain volume ({value:.2f}) is commonly associated with "
                "brain atrophy and increased the estimated dementia risk."
            )

        else:
            text = (
                f"A relatively preserved whole brain volume ({value:.2f}) reduced "
                "the estimated dementia risk."
            )

    elif feature == "education_years":

        if value >= 16:
            text = (
                f"{int(value)} years of education may provide greater cognitive reserve, "
                "which lowered the model's estimated dementia risk."
            )

        else:
            text = (
                f"{int(value)} years of education provided less cognitive reserve "
                "relative to many patients in the training data."
            )

    elif feature == "estimated_intracranial_volume":

        text = (
            f"Estimated intracranial volume ({value:.0f}) had a modest influence "
            "on the prediction."
        )

    elif feature == "atlas_scaling_factor":

        text = (
            f"Atlas Scaling Factor ({value:.2f}) contributed slightly to the "
            "overall prediction."
        )

    elif feature == "socioeconomic_status":

        text = (
            f"Socioeconomic status ({value}) had a relatively small contribution "
            "to the model's prediction."
        )

    elif feature == "gender_male":

        if value == 1:
            text = (
                "The patient was male. Gender had only a small influence on the prediction."
            )
        else:
            text = (
                "The patient was female. Gender had only a small influence on the prediction."
            )

    else:

        text = f"{name} influenced the model prediction."

    return {
        "feature": name,
        "value": value,
        "impact": shap_value,
        "direction": direction,
        "text": text,
    }


def predict_patient(patient_dict):

    patient = pd.DataFrame([patient_dict])


    # Probabilities
    probabilities = model.predict_proba(patient)[0]

    # Prediction (tuned decision threshold, not the default 0.5)
    prediction = int(probabilities[1] >= DECISION_THRESHOLD)

    dementia_risk = float(probabilities[1] * 100)

    if prediction == 1:
        label = "Demented"
        confidence = dementia_risk
    else:
        label = "Nondemented"
        confidence = 100 - dementia_risk

    # SHAP

    shap_values = explainer(patient)
    explanation_rows = []

    for feature, value, impact in zip(
        patient.columns,
        patient.iloc[0],
        shap_values.values[0]
    ):

        explanation_rows.append(
            explain_feature(
                feature,
                value,
                impact
            )
        )


    explanations = pd.DataFrame(explanation_rows)
    explanations["strength"] = explanations["impact"].abs()

    # strongest influences
    explanations["abs_impact"] = explanations["impact"].abs()
    

    explanations = (
        explanations
        .sort_values(
            "abs_impact",
            ascending=False
        )
        .drop(columns=["abs_impact"])
    )

    return {
        "label": label,
        "risk": dementia_risk,
        "confidence": confidence,
        "importance": explanations
    }