import joblib
import pandas as pd
import numpy as np

model = joblib.load("models/clinician_model.pkl")
explainer = joblib.load("models/clinician_shap_explainer.pkl")


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

    # Direction of SHAP contribution
    if shap_value > 0:
        direction = "increased"
        arrow = "⬆"
    else:
        direction = "decreased"
        arrow = "⬇"


    # Medical context
    explanations = {

        "age":
            f"{name} ({int(value)} years) {direction} the estimated dementia likelihood.",

        "mmse_score":
            f"{name} ({value:.0f}/30) contributed to the model's dementia risk estimate",

        "normalized_whole_brain_volume":
            f"{name} ({value:.2f}) {direction} the estimated dementia likelihood.",

        "education_years":
            f"{name} ({int(value)} years) influenced the model's prediction.",

        "estimated_intracranial_volume":
            f"{name} ({value:.0f}) influenced the model's prediction.",

        "atlas_scaling_factor":
            f"{name} ({value:.2f}) influenced the model's prediction.",

        "socioeconomic_status":
            f"{name} ({value}) influenced the model's prediction.",

        "gender_male":
            f"{name} influenced the model's prediction."
    }


    return {
        "feature": name,
        "value": value,
        "impact": shap_value,
        "direction": direction,
        "text": explanations.get(
            feature,
            f"{name} influenced the model prediction."
        )
    }



def predict_patient(patient_dict):

    patient = pd.DataFrame([patient_dict])


    # Prediction
    prediction = int(model.predict(patient)[0])


    # Probabilities
    probabilities = model.predict_proba(patient)[0]

    dementia_probability = probabilities[1]
    prediction_probability = probabilities[prediction]


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


    label = (
        "Demented"
        if prediction == 1
        else "Nondemented"
    )


    return {

        "label": label,

        # dementia probability
        "risk": dementia_probability * 100,

        # probability of chosen class
        "confidence": prediction_probability * 100,

        "importance": explanations
    }