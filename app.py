"""HeartGuard - Early Heart Disease Risk Prediction with Explainable AI.

Main Streamlit application entry point.
"""

import streamlit as st

from config.settings import PROJECT_NAME, PROJECT_VERSION

st.set_page_config(
    page_title=f"{PROJECT_NAME} - Heart Disease Risk Prediction",
    page_icon="heart",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("HEARTGUARD")
st.subheader("Early Heart Disease Risk Prediction with Explainable AI")

st.markdown(
    "AI-powered research prototype for multimodal heart disease risk assessment."
)

st.divider()

st.markdown(
    "**Disclaimer:** HeartGuard is an academic/research prototype and is not a "
    "medical diagnostic system. Model predictions are experimental estimates based "
    "on the provided data and should not replace evaluation or advice from a "
    "qualified healthcare professional."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### Clinical Risk")
        st.markdown("Coming in Phase 6")
        st.caption("Machine learning-based clinical risk prediction")

    with st.container(border=True):
        st.markdown("### Explainable AI")
        st.markdown("Coming in Phase 7")
        st.caption("SHAP-based prediction explanations")

with col2:
    with st.container(border=True):
        st.markdown("### Lifestyle Risk")
        st.markdown("Coming in Phase 8")
        st.caption("NLP-based lifestyle risk analysis")

    with st.container(border=True):
        st.markdown("### Emergency Alerts")
        st.markdown("Coming in Phase 10")
        st.caption("Twilio SMS notification system")

st.divider()

st.markdown(f"**Version:** {PROJECT_VERSION}")
st.markdown("**Status:** Phase 1 - Project Foundation")
