"""Registration page for HeartGuard (Phase 9).

Patient self-registration only. The ADMIN role is never selectable
from this page — admin accounts must be seeded via scripts/create_admin.py.
"""

from __future__ import annotations

import streamlit as st

from src.auth.auth_service import register_user
from src.auth.session_manager import is_authenticated
from src.security.audit_logger import log_event

st.set_page_config(
    page_title="HeartGuard — Register",
    page_icon="❤️",
    layout="centered",
)

from src.ui.theme import inject_global_theme
inject_global_theme()

# Redirect if already logged in
if is_authenticated():
    st.switch_page("pages/dashboard.py")

st.markdown(
    """
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size:2.5rem; margin-bottom:0;">❤️ HeartGuard</h1>
        <p style="color:#888; margin-top:0.3rem;">Create your Patient Account</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "**Privacy Notice:** HeartGuard is an academic/research prototype. "
    "Do not enter real patient information into a public/demo deployment."
)
st.divider()

with st.form("register_form", clear_on_submit=False):
    name = st.text_input("Full Name", placeholder="Jane Smith", key="reg_name")
    email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
    password = st.text_input(
        "Password",
        type="password",
        placeholder="Minimum 8 characters",
        key="reg_password",
        help="Minimum 8 characters required.",
    )
    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password",
        key="reg_confirm",
    )

    # Role is always PATIENT for self-registration — not shown as a selectable field
    st.caption("Account type: **Patient** (all self-registered accounts are Patient accounts)")

    submit = st.form_submit_button(
        "Create Account", use_container_width=True, type="primary"
    )

if submit:
    # Collect values; do NOT log password or confirm_password
    with st.spinner("Creating your account…"):
        try:
            user = register_user(
                name=name,
                email=email,
                password=password,
                confirm_password=confirm_password,
            )
            log_event(
                event_type="registration",
                status="SUCCESS",
                user_id=user["id"],
                role=user["role"],
                detail="Patient self-registration",
            )
            st.success(
                f"✅ Account created! Welcome, **{user['name']}**. "
                "Please log in to continue."
            )
            st.page_link("pages/login.py", label="Go to Login →")
        except ValueError as exc:
            log_event(
                event_type="registration",
                status="FAILURE",
                detail="Validation error during registration",
            )
            # Show the validation error (these are safe, non-credential messages)
            st.error(str(exc))
        except Exception:
            log_event(
                event_type="registration",
                status="FAILURE",
                detail="Unexpected error during registration",
            )
            st.error("Something went wrong. Please try again.")

st.divider()
st.markdown("Already have an account?")
st.page_link("pages/login.py", label="← Back to Login")
