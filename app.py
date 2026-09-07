"""HeartGuard - Early Heart Disease Risk Prediction with Explainable AI.

Main Streamlit application entry point (Phase 9 — Security Hardened).
Redirects unauthenticated users to the login page and provides a
role-aware home screen with navigation and logout.
"""

import streamlit as st

from config.settings import DEMO_MODE, PROJECT_NAME, PROJECT_VERSION
from src.auth.authorization import is_admin
from src.auth.session_manager import (
    clear_session,
    get_current_user,
    is_authenticated,
)
from src.security.audit_logger import log_event

st.set_page_config(
    page_title=f"{PROJECT_NAME} - Heart Disease Risk Prediction",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Authentication gate
# ---------------------------------------------------------------------------
if not is_authenticated():
    st.switch_page("pages/login.py")

current_user = get_current_user()

# ---------------------------------------------------------------------------
# Sidebar — user info & logout
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"**{current_user['name']}**")
    st.caption(f"Role: `{current_user['role']}`")
    st.divider()
    if st.button("🚪 Log Out", use_container_width=True):
        log_event(
            event_type="logout",
            status="SUCCESS",
            user_id=current_user["id"],
            role=current_user["role"],
        )
        clear_session()
        st.switch_page("pages/login.py")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.title("❤️ HEARTGUARD")
st.subheader("Early Heart Disease Risk Prediction with Explainable AI")

if DEMO_MODE:
    st.info(
        "🟦 **Demo Mode** — External SMS notifications are disabled. "
        "All risk assessments and explainability features are fully operational."
    )

st.markdown(
    "AI-powered research prototype for multimodal heart disease risk assessment."
)

st.divider()

st.markdown(
    "> **Disclaimer:** HeartGuard is an academic/research prototype and is not a "
    "medical diagnostic system. Model predictions are experimental estimates based "
    "on the provided data and should not replace evaluation or advice from a "
    "qualified healthcare professional.\n\n"
    "> **Privacy Notice:** Do not enter real patient information into a public/demo deployment."
)

st.divider()

# ---------------------------------------------------------------------------
# Navigation cards
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 🩺 Risk Assessment")
        st.markdown("Multimodal cardiovascular risk prediction (Clinical + Lifestyle)")
        st.page_link("pages/risk_assessment.py", label="Open Risk Assessment →")

    with st.container(border=True):
        st.markdown("### 🧬 Explainable AI")
        st.markdown("SHAP-based feature importance and patient-level explanations")
        st.page_link("pages/explainable_ai.py", label="Open Explainable AI →")

with col2:
    with st.container(border=True):
        st.markdown("### 🏃 Lifestyle Analyzer")
        st.markdown("NLP-based lifestyle cardiovascular risk scoring")
        st.page_link("pages/lifestyle_analyzer.py", label="Open Lifestyle Analyzer →")

    with st.container(border=True):
        st.markdown("### 📊 Dashboard")
        st.markdown("System status, data pipeline, and model information")
        st.page_link("pages/dashboard.py", label="Open Dashboard →")

if is_admin():
    st.divider()
    st.markdown("#### Admin Tools")
    a1, a2, a3 = st.columns(3)
    with a1:
        st.page_link("pages/admin.py", label="🛡️ Admin Dashboard →")
    with a2:
        st.page_link("pages/model_performance.py", label="📈 Model Performance →")
    with a3:
        st.page_link("pages/security.py", label="🔐 Security Status →")

st.divider()
st.markdown(f"**Version:** {PROJECT_VERSION} · **Status:** Phase 9 — Security Hardened")
