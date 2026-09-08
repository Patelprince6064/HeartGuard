"""Shared sidebar navigation component for HeartGuard (Phase 18).

Provides a consistent, role-based sidebar used across all pages.
Eliminates the sidebar duplication that existed across 15 page files.
"""

from __future__ import annotations

import streamlit as st

from src.auth.authorization import is_admin, is_reviewer
from src.auth.session_manager import clear_session, get_current_user
from src.security.audit_logger import log_event


def render_sidebar() -> None:
    """Render the standard HeartGuard sidebar with user info, navigation, and logout.

    This should be called at the top of every page (after ``set_page_config``).
    The sidebar includes:
    - User name and role
    - Navigation links (role-gated)
    - Logout button
    """
    current_user = get_current_user()

    with st.sidebar:
        # ── Brand ────────────────────────────────────────────────────────
        st.markdown("### ❤️ HeartGuard")

        # ── User info ────────────────────────────────────────────────────
        if current_user:
            st.markdown(f"**{current_user.get('name', 'User')}**")
            st.caption(f"Role: `{current_user.get('role', 'PATIENT')}`")
        st.divider()

        # ── Navigation ───────────────────────────────────────────────────
        st.markdown("##### Navigation")

        st.page_link("pages/dashboard.py", label="📊 Dashboard", use_container_width=True)
        st.page_link("pages/risk_assessment.py", label="🩺 New Assessment", use_container_width=True)
        st.page_link("pages/lifestyle_analyzer.py", label="🏃 Lifestyle Analyzer", use_container_width=True)
        st.page_link("pages/history.py", label="📜 History & Reports", use_container_width=True)
        st.page_link("pages/explainable_ai.py", label="🧬 Explainable AI", use_container_width=True)
        st.page_link("pages/patient_analytics.py", label="📈 My Analytics", use_container_width=True)

        if is_reviewer():
            st.divider()
            st.markdown("##### Clinical Tools")
            st.page_link("pages/review.py", label="🩺 Doctor Review", use_container_width=True)

        if is_admin():
            st.divider()
            st.markdown("##### Administration")
            st.page_link("pages/admin.py", label="🛡️ Admin Dashboard", use_container_width=True)
            st.page_link("pages/analytics_dashboard.py", label="📈 Analytics Dashboard", use_container_width=True)
            st.page_link("pages/model_monitoring.py", label="🔬 Model Monitoring", use_container_width=True)
            st.page_link("pages/model_performance.py", label="📊 Model Performance", use_container_width=True)

        st.divider()
        st.page_link("pages/security.py", label="🔐 Security & Profile", use_container_width=True)
        st.page_link("pages/about.py", label="ℹ️ About", use_container_width=True)

        # ── Logout ───────────────────────────────────────────────────────
        st.divider()
        if st.button("🚪 Log Out", use_container_width=True, key="sidebar_logout"):
            if current_user:
                log_event(
                    event_type="logout",
                    status="SUCCESS",
                    user_id=current_user.get("id"),
                    role=current_user.get("role"),
                )
            clear_session()
            st.switch_page("pages/login.py")
