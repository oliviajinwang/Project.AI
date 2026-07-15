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
def _load_metrics():
    # Group-aware cross-validated accuracy/macro-F1/AUC, computed separately
    # from training (see models/clinical_metrics.json). This is a 3-class
    # problem (Nondemented / Demented / Converted) with a rare third class
    # (37 of 373 rows) -- accuracy alone can look fine while the model still
    # does poorly on Converted, which is why macro_f1 is also tracked.
    with open("models/clinical_metrics.json") as f:
        return json.load(f)


model = _load_model()
explainer = _load_explainer()
MODEL_METRICS = _load_metrics()

CLASS_LABELS = {0: "Nondemented", 1: "Demented", 2: "Converted"}
FEATURE_ORDER = [
    "gender_male",
    "age",
    "education_years",
    "socioeconomic_status",
    "mmse_score",
    "estimated_intracranial_volume",
    "normalized_whole_brain_volume",
    "atlas_scaling_factor",
]

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

    patient = pd.DataFrame([patient_dict])[FEATURE_ORDER]

    probabilities = model.predict_proba(patient)[0]

    prediction = int(np.argmax(probabilities))
    label = CLASS_LABELS[prediction]

    dementia_risk = float((1 - probabilities[0]) * 100)
    confidence = float(probabilities[prediction] * 100)

    shap_values = explainer(patient)
    shap_array = np.asarray(shap_values.values)

    if shap_array.ndim == 3:
        if shap_array.shape[1] == patient.shape[1]:
            # Shape: samples × features × classes
            predicted_class_shap = shap_array[0, :, prediction]

        elif shap_array.shape[2] == patient.shape[1]:
            # Shape: samples × classes × features
            predicted_class_shap = shap_array[0, prediction, :]

        else:
            raise ValueError(
                f"Unexpected SHAP shape: {shap_array.shape}. "
                f"Expected {patient.shape[1]} features."
            )

    elif shap_array.ndim == 2:
        if shap_array.shape[1] != patient.shape[1]:
            raise ValueError(
                f"Unexpected SHAP shape: {shap_array.shape}. "
                f"Expected {patient.shape[1]} features."
            )

        predicted_class_shap = shap_array[0]

    elif shap_array.ndim == 1:
        if shap_array.shape[0] != patient.shape[1]:
            raise ValueError(
                f"Unexpected SHAP shape: {shap_array.shape}. "
                f"Expected {patient.shape[1]} features."
            )

        predicted_class_shap = shap_array

    else:
        raise ValueError(
            f"Unsupported SHAP output shape: {shap_array.shape}"
        )

    explanation_rows = []

    for feature, value, impact in zip(
        patient.columns,
        patient.iloc[0],
        predicted_class_shap
    ):
        explanation_rows.append(
            explain_feature(
                feature,
                value,
                float(impact)
            )
        )

    explanations = pd.DataFrame(explanation_rows)
    explanations["strength"] = explanations["impact"].abs()

    explanations = explanations.sort_values(
        "strength",
        ascending=False
    )

    return {
        "label": label,
        "risk": dementia_risk,
        "confidence": confidence,
        "importance": explanations
    }