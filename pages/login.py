"""Login page for HeartGuard (Phase 9).

Provides secure email/password authentication with:
  - Generic error messages (no email-existence leakage)
  - Session-state rate limiting
  - Audit logging on success/failure
  - Redirect to dashboard on success
"""

from __future__ import annotations

import streamlit as st

from src.auth.auth_service import authenticate_user
from src.auth.session_manager import create_session, is_authenticated
from src.security.audit_logger import log_event
from src.security.rate_limiter import (
    is_rate_limited,
    record_failed_attempt,
    reset_attempts,
    seconds_remaining,
)

st.set_page_config(
    page_title="HeartGuard — Login",
    page_icon="❤️",
    layout="centered",
)

from src.ui.theme import inject_global_theme
inject_global_theme()

# ---------------------------------------------------------------------------
# Redirect if already authenticated
# ---------------------------------------------------------------------------
if is_authenticated():
    st.switch_page("pages/dashboard.py")

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size:2.5rem; margin-bottom:0;">❤️ HeartGuard</h1>
        <p style="color:#888; margin-top:0.3rem;">Early Heart Disease Risk Prediction</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Sign In")
st.caption(
    "HeartGuard is an academic/research prototype. "
    "Do not enter real patient information into a public/demo deployment."
)
st.divider()

# ---------------------------------------------------------------------------
# Rate-limit check
# ---------------------------------------------------------------------------
if is_rate_limited():
    secs = seconds_remaining()
    st.error(
        f"⛔ Too many failed login attempts. "
        f"Please wait {secs} second{'s' if secs != 1 else ''} before trying again."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Login form
# ---------------------------------------------------------------------------
with st.form("login_form", clear_on_submit=False):
    email = st.text_input("Email", placeholder="you@example.com", key="login_email")
    password = st.text_input(
        "Password", type="password", placeholder="Your password", key="login_password"
    )
    submit = st.form_submit_button("Log In", use_container_width=True, type="primary")

if submit:
    # Basic presence check — detailed validation happens in authenticate_user
    if not email or not password:
        st.error("Invalid email or password.")
    else:
        with st.spinner("Signing in…"):
            user = authenticate_user(email.strip(), password)

        if user:
            create_session(user)
            reset_attempts()
            log_event(
                event_type="login_success",
                status="SUCCESS",
                user_id=user["id"],
                role=user["role"],
                detail="Login via login page",
            )
            st.success("Login successful! Redirecting…")
            st.switch_page("pages/dashboard.py")
        else:
            attempts = record_failed_attempt()
            log_event(
                event_type="login_failure",
                status="FAILURE",
                detail="Invalid credentials submitted",
            )
            # ALWAYS use a generic message — never reveal whether email exists
            st.error("Invalid email or password.")

st.divider()
st.markdown("Don't have an account?")
st.page_link("pages/register.py", label="Register as a Patient →")
