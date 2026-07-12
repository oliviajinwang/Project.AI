import streamlit as st

# Mirrors the exact fields the existing "See what happens if..." What-If
# simulators already treat as quickly modifiable (deliberately excludes
# diabetes, same as those simulators -- it isn't a "quick" lifestyle change).
# Display names match FEATURE_DESCRIPTIONS in src/predict_lifestyle.py, since
# that's the column the SHAP importance dataframe is keyed on.
MODIFIABLE_LIFESTYLE_FIELDS = {
    "smoking": ("Smoking", "quitting smoking"),
    "hypertension": ("Hypertension", "controlling your blood pressure"),
    "high_cholesterol": ("High Cholesterol", "controlling your cholesterol"),
}


def render_lifestyle_action_plan(result: dict, original_inputs: dict, predict_fn, key_prefix: str = "") -> None:
    """Turns the SHAP risk-driver breakdown into a concrete, model-backed
    action plan. Every number shown is re-derived by calling predict_fn with
    one factor flipped off -- not a generic claim, so it's always something
    this specific model actually produced for this specific patient.
    """
    importance = result["importance"]
    flagged = []
    for field, (display_name, action_phrase) in MODIFIABLE_LIFESTYLE_FIELDS.items():
        if not original_inputs.get(field):
            continue
        row = importance[importance["feature"] == display_name]
        if row.empty or row.iloc[0]["impact"] <= 0:
            continue
        flagged.append((field, display_name, action_phrase, float(row.iloc[0]["impact"])))

    st.markdown("---")
    st.subheader("Your Personalized Action Plan")

    if not flagged:
        st.caption(
            "None of the modifiable factors this model tracks (smoking, blood "
            "pressure, cholesterol) are currently flagged as increasing the "
            "estimated risk above."
        )
        return

    st.caption(
        "Ranked by how much each factor is estimated to be contributing to the "
        "risk above, with the model's own estimate of what addressing it alone "
        "could do -- not a general statistic, a number this model produced for "
        "these specific answers."
    )
    flagged.sort(key=lambda item: item[3], reverse=True)
    for field, display_name, action_phrase, impact in flagged:
        whatif_inputs = dict(original_inputs)
        whatif_inputs[field] = 0
        whatif_result = predict_fn(whatif_inputs)
        delta = result["risk"] - whatif_result["risk"]
        with st.container(border=True, key=f"{key_prefix}action_{field}"):
            st.markdown(f"**{display_name}**")
            if delta > 0.05:
                st.write(
                    f"This model estimates {action_phrase} could lower the "
                    f"estimated risk from **{result['risk']:.1f}%** to "
                    f"**{whatif_result['risk']:.1f}%** (a {delta:.1f} percentage-point "
                    f"drop), holding everything else the same."
                )
            else:
                st.write(
                    f"This factor is contributing to the estimated risk, though "
                    f"this model doesn't project a large change from addressing "
                    f"it alone."
                )
            st.caption("Not medical advice -- discuss any changes with a physician.")
