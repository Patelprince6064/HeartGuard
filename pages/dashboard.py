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

# Resolve best model dynamically
best_model_name = "None"
if best_model_path.exists():
    try:
        with open(best_model_path, "r", encoding="utf-8") as f:
            best_info = json.load(f)
        best_model_name = best_info.get("model_name", "logistic_regression").replace("_", " ").title()
    except Exception:
        best_model_name = "Logistic Regression"

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.markdown("### Clinical ML Model")
        st.markdown(f"**{best_model_name}**")
        if best_model_path.exists():
            st.success("READY")
        else:
            st.warning("Not Trained")

with col2:
    with st.container(border=True):
        st.markdown("### SHAP Explainability")
        st.markdown("**Tree & Linear Explainer**")
        if (REPORT_DIRECTORY / "explainability").exists() or best_model_path.exists():
            st.success("READY")
        else:
            st.info("NOT AVAILABLE")

with col3:
    with st.container(border=True):
        st.markdown("### Lifestyle Analyzer")
        st.markdown("**Rule-Based NLP Lexicon**")
        st.success("READY")

with col4:
    with st.container(border=True):
        st.markdown("### Multimodal Engine")
        st.markdown("**70% Clinical + 30% Lifestyle**")
        if best_model_path.exists():
            st.success("READY")
        else:
            st.warning("Requires ML Model")

st.divider()

if best_model_path.exists():
    st.success("Phase 1 through Phase 7 Complete — Multimodal Risk Engine, Clinical Models, SHAP, and Lifestyle NLP are operational.")
else:
    st.info("Train the clinical models to activate the full Multimodal Risk Engine.")
