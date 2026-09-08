"""Shared clinical input form component for HeartGuard (Phase 18).

Deduplicates the clinical/lifestyle input form used across
``risk_assessment.py`` and ``explainable_ai.py``.

SAFETY RULE:
  This component only collects user input. It does NOT perform
  any medical assessment or diagnosis.
"""

from __future__ import annotations

from typing import Any
import streamlit as st


# ── Option Maps ──────────────────────────────────────────────────────────────

SEX_OPTIONS = {"0": "Female", "1": "Male"}

CHEST_PAIN_OPTIONS = {
    "0": "Typical Angina",
    "1": "Atypical Angina",
    "2": "Non-Anginal Pain",
    "3": "Asymptomatic",
}

FBS_OPTIONS = {"0": "False (≤120 mg/dl)", "1": "True (>120 mg/dl)"}

RESTING_ECG_OPTIONS = {
    "0": "Normal",
    "1": "ST-T Wave Abnormality",
    "2": "Left Ventricular Hypertrophy",
}

EXERCISE_ANGINA_OPTIONS = {"0": "No", "1": "Yes"}

FORM_HELP = {
    "age": "Patient age in years (29-77 typical range)",
    "sex": "Biological sex (used in clinical feature set)",
    "chest_pain": "Type of chest pain experienced",
    "resting_bp": "Resting blood pressure in mm Hg on admission",
    "cholesterol": "Serum cholesterol in mg/dl",
    "fasting_bs": "Fasting blood sugar > 120 mg/dl",
    "resting_ecg": "Resting electrocardiographic results",
    "max_hr": "Maximum heart rate achieved during exercise",
    "exercise_angina": "Exercise-induced angina",
    "st_depression": "ST depression induced by exercise relative to rest",
    "num_vessels": "Number of major vessels colored by fluoroscopy (0-3)",
}


def render_clinical_inputs(key_prefix: str = "clinical") -> dict[str, Any]:
    """Render the clinical input form in a 3-column layout.

    Returns:
        Dictionary with all clinical input values.
    """
    st.markdown("#### Clinical Measurements")
    st.caption("Enter the patient's clinical measurements for model-based risk assessment.")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=55,
            step=1,
            help=FORM_HELP["age"],
            key=f"{key_prefix}_age",
        )
        sex = st.selectbox(
            "Sex",
            options=list(SEX_OPTIONS.keys()),
            format_func=lambda x: SEX_OPTIONS[x],
            help=FORM_HELP["sex"],
            key=f"{key_prefix}_sex",
        )
        chest_pain = st.selectbox(
            "Chest Pain Type",
            options=list(CHEST_PAIN_OPTIONS.keys()),
            format_func=lambda x: CHEST_PAIN_OPTIONS[x],
            help=FORM_HELP["chest_pain"],
            key=f"{key_prefix}_chest_pain",
        )

    with col2:
        resting_bp = st.number_input(
            "Resting Blood Pressure (mm Hg)",
            min_value=60,
            max_value=250,
            value=130,
            step=1,
            help=FORM_HELP["resting_bp"],
            key=f"{key_prefix}_bp",
        )
        cholesterol = st.number_input(
            "Serum Cholesterol (mg/dl)",
            min_value=100,
            max_value=600,
            value=200,
            step=1,
            help=FORM_HELP["cholesterol"],
            key=f"{key_prefix}_chol",
        )
        fasting_bs = st.selectbox(
            "Fasting Blood Sugar > 120 mg/dl",
            options=list(FBS_OPTIONS.keys()),
            format_func=lambda x: FBS_OPTIONS[x],
            help=FORM_HELP["fasting_bs"],
            key=f"{key_prefix}_fbs",
        )

    with col3:
        resting_ecg = st.selectbox(
            "Resting ECG",
            options=list(RESTING_ECG_OPTIONS.keys()),
            format_func=lambda x: RESTING_ECG_OPTIONS[x],
            help=FORM_HELP["resting_ecg"],
            key=f"{key_prefix}_ecg",
        )
        max_hr = st.number_input(
            "Max Heart Rate",
            min_value=60,
            max_value=250,
            value=150,
            step=1,
            help=FORM_HELP["max_hr"],
            key=f"{key_prefix}_hr",
        )
        exercise_angina = st.selectbox(
            "Exercise-Induced Angina",
            options=list(EXERCISE_ANGINA_OPTIONS.keys()),
            format_func=lambda x: EXERCISE_ANGINA_OPTIONS[x],
            help=FORM_HELP["exercise_angina"],
            key=f"{key_prefix}_angina",
        )

    # Additional row for remaining fields
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st_depression = st.number_input(
            "ST Depression (0.0 - 6.2)",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
            format="%.1f",
            help=FORM_HELP["st_depression"],
            key=f"{key_prefix}_stdep",
        )

    with row2_col2:
        num_vessels = st.number_input(
            "Number of Major Vessels (0-3)",
            min_value=0,
            max_value=3,
            value=0,
            step=1,
            help=FORM_HELP["num_vessels"],
            key=f"{key_prefix}_vessels",
        )

    return {
        "age": int(age),
        "sex": str(sex),
        "chest_pain_type": str(chest_pain),
        "resting_bp": int(resting_bp),
        "cholesterol": int(cholesterol),
        "fasting_blood_sugar": str(fasting_bs),
        "resting_ecg": str(resting_ecg),
        "max_heart_rate": int(max_hr),
        "exercise_angina": str(exercise_angina),
        "st_depression": float(st_depression),
        "num_major_vessels": int(num_vessels),
    }
