import random

LIFESTYLE_LABELS = ["Low Risk", "High Risk"]
CLINICAL_LABELS = ["Nondemented", "Demented", "Converted"]


def get_mock_prediction(kind: str = "lifestyle") -> tuple[str, float]:
    """Placeholder for model.predict_proba(). Swap the body of this
    function for a real model call once patient_model.pkl / clinician_model.pkl
    exist — callers elsewhere don't need to change."""
    labels = LIFESTYLE_LABELS if kind == "lifestyle" else CLINICAL_LABELS
    label = random.choice(labels)
    confidence = random.uniform(55, 98)
    return label, confidence
