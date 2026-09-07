"""Dashboard page for HeartGuard."""

import streamlit as st

from config.settings import (
    MODEL_DIRECTORY,
    PROCESSED_DATA_DIRECTORY,
    PROJECT_NAME,
    RAW_DATA_DIRECTORY,
    REPORT_DIRECTORY,
)

st.title("Dashboard")

st.markdown(
    "**Disclaimer:** HeartGuard is an academic/research prototype and is not a "
    "medical diagnostic system. Model predictions are experimental estimates based "
    "on the provided data and should not replace evaluation or advice from a "
    "qualified healthcare professional."
)

st.divider()

# --- Data Pipeline Status ---
st.markdown("### Data Pipeline")

cleveland_path = RAW_DATA_DIRECTORY / "heart.csv"
framingham_path = RAW_DATA_DIRECTORY / "framingham.csv"

col_a, col_b = st.columns(2)

with col_a:
    with st.container(border=True):
        st.markdown("**Cleveland Dataset**")
        if cleveland_path.exists():
            st.success("Ready")
            st.caption(f"Path: {cleveland_path.name}")
        else:
            st.warning("Not Found")
            st.caption(f"Place {cleveland_path.name} in data/raw/")

with col_b:
    with st.container(border=True):
        st.markdown("**Framingham Dataset**")
        if framingham_path.exists():
            st.success("Ready")
            st.caption(f"Path: {framingham_path.name}")
        else:
            st.info("Optional — Not Found")
            st.caption(f"Place {framingham_path.name} in data/raw/")

# Pipeline and preprocessing status
col_c, col_d = st.columns(2)

with col_c:
    with st.container(border=True):
        st.markdown("**Data Pipeline**")
        preprocessor_path = MODEL_DIRECTORY / "preprocessor.pkl"
        train_path = PROCESSED_DATA_DIRECTORY / "cleveland_train.csv"
        if preprocessor_path.exists() and train_path.exists():
            st.success("Ready")
            st.caption("Preprocessor fitted, train/test data generated")
        else:
            st.warning("Not Ready")
            st.caption("Run pipeline to generate ML-ready data")

with col_d:
    with st.container(border=True):
        st.markdown("**ML Training**")
        best_model_path = REPORT_DIRECTORY / "best_model.json"
        if best_model_path.exists():
            st.success("Complete")
            with open(best_model_path, "r") as f:
                import json
                best = json.load(f)
            st.caption(f"Best model: {best.get('model_name', 'unknown')}")
        elif preprocessor_path.exists():
            st.info("Not Started")
            st.caption("Data pipeline ready — run training")
        else:
            st.info("Not Started")
            st.caption("Complete data pipeline first")

st.divider()

# --- Project Overview ---
st.markdown("### Project Overview")

st.markdown(
    f"{PROJECT_NAME} is an AI-powered research prototype for early heart disease "
    "risk prediction. The system combines clinical data analysis, machine learning, "
    "explainable AI, and lifestyle text analysis to provide comprehensive heart "
    "disease risk assessments."
)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### Risk Prediction Engine")
        st.markdown("ML-based clinical risk assessment")
        if best_model_path.exists():
            st.success("Phase 4 Complete")
        else:
            st.caption("Phase 4-6")

with col2:
    with st.container(border=True):
        st.markdown("### Explainability Module")
        st.markdown("SHAP-based prediction explanations")
        if (REPORT_DIRECTORY / "explainability").exists():
            st.success("Phase 5 Complete")
        else:
            st.caption("Phase 5")

with col3:
    with st.container(border=True):
        st.markdown("### Lifestyle Analyzer")
        st.markdown("NLP-based lifestyle risk analysis")
        st.caption("Phase 8")

st.divider()

if best_model_path.exists():
    st.success("Phase 4 & 5 complete — Models trained and Explainable AI ready.")
else:
    st.info("Phase 3 complete — Data pipeline and EDA ready. Model training coming in Phase 4.")
