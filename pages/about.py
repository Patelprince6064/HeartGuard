"""About page for HeartGuard (Phase 9)."""

import streamlit as st

from config.settings import PROJECT_NAME, PROJECT_VERSION
from src.auth.authorization import require_authentication
from src.auth.session_manager import get_current_user
from src.ui import render_sidebar, inject_global_theme

st.set_page_config(page_title="About HeartGuard", layout="wide")

# ── Authorization ────────────────────────────────────────────────────────────
require_authentication()
current_user = get_current_user()

render_sidebar()
inject_global_theme()

st.title("About HeartGuard")

st.info(
    "🔒 **Privacy Notice:** HeartGuard is an academic/research prototype. "
    "Do not enter real patient information into a public/demo deployment."
)

st.markdown(
    "**Disclaimer:** HeartGuard is an academic/research prototype and is not a "
    "medical diagnostic system. Model predictions are experimental estimates based "
    "on the provided data and should not replace evaluation or advice from a "
    "qualified healthcare professional."
)

st.divider()

st.markdown("### Overview")

st.markdown(
    f"**{PROJECT_NAME}** is an academic/research prototype for early heart disease "
    "risk assessment. The system combines multiple modalities to provide comprehensive "
    "risk evaluations."
)

st.markdown("### Project Objective")

st.markdown(
    "HeartGuard aims to develop a multimodal heart disease risk prediction system "
    "that combines:"
)

st.markdown(
    "1. **Clinical data analysis** using machine learning\n"
    "2. **Explainable predictions** using SHAP\n"
    "3. **Lifestyle risk assessment** through NLP\n"
    "4. **Unified risk scoring** combining clinical and lifestyle factors\n"
    "5. **Emergency alerts** for critical risk cases"
)

st.markdown("### Main Modules")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("#### Risk Prediction Engine")
        st.markdown("ML-based clinical risk assessment using ensemble methods")

    with st.container(border=True):
        st.markdown("#### Explainability Module")
        st.markdown("SHAP-based prediction explanations for transparency")

with col2:
    with st.container(border=True):
        st.markdown("#### Lifestyle Analyzer")
        st.markdown("NLP-based lifestyle risk factor extraction and scoring")

    with st.container(border=True):
        st.markdown("#### Emergency Alert System")
        st.markdown("Twilio SMS notifications for critical risk cases")

st.markdown("### Technology Stack")

st.markdown(
    "- **Language:** Python 3.12+\n"
    "- **Web Framework:** Streamlit\n"
    "- **ML Libraries:** scikit-learn, XGBoost, TensorFlow\n"
    "- **Explainability:** SHAP\n"
    "- **NLP:** NLTK\n"
    "- **Visualization:** Matplotlib, Plotly\n"
    "- **Notifications:** Twilio\n"
    "- **Testing:** pytest"
)

st.divider()

st.markdown(f"**Version:** {PROJECT_VERSION}")
