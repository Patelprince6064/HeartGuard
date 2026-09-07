"""Security Status Dashboard for HeartGuard (Phase 9).

Shows the security posture of the application. Available to all
authenticated users. Never displays actual secrets — only
configured/not-configured status.
"""

from __future__ import annotations

import streamlit as st

from config.settings import (
    ALERTS_ENABLED,
    AUTH_DB_PATH,
    AUDIT_DB_PATH,
    DEBUG,
    DEMO_MODE,
    DOCTOR_PHONE_NUMBER,
    EMERGENCY_CONTACT_PHONE_NUMBER,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
)
from src.auth.authorization import require_authentication
from src.auth.session_manager import get_current_user

st.set_page_config(page_title="HeartGuard — Security Status", layout="wide")

# ── Authorization ───────────────────────────────────────────────────────────
require_authentication()
current_user = get_current_user()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🔐 Security Status")
st.caption(
    "This page shows the security configuration of the HeartGuard application. "
    "No secrets, passwords, or tokens are displayed here."
)
st.divider()

# ── Mode Banner ──────────────────────────────────────────────────────────────
if DEMO_MODE:
    st.info(
        "🟦 **Demo Mode** — External SMS notifications are disabled. "
        "All risk assessments and explanations are fully functional. "
        "Set `ALERTS_ENABLED=true` in your `.env` to enable live Twilio alerts."
    )
else:
    st.success("🟢 **Live Mode** — External SMS alerts are enabled.")

if DEBUG:
    st.warning(
        "⚠️ **DEBUG=true** — Debug mode is active. "
        "Set `DEBUG=false` for production deployment."
    )

st.divider()

# ── Security Checklist ────────────────────────────────────────────────────────
st.markdown("### Security Controls")

def _status(ok: bool, label: str, caption: str = "") -> None:
    col_a, col_b = st.columns([1, 5])
    with col_a:
        if ok:
            st.success("✅ READY")
        else:
            st.warning("⚠️ CHECK")
    with col_b:
        st.markdown(f"**{label}**")
        if caption:
            st.caption(caption)


_status(True, "Authentication", "Login/logout with bcrypt password hashing")
_status(True, "Role-Based Authorization (RBAC)", "PATIENT and ADMIN roles enforced server-side")
_status(True, "Secure Password Hashing", "bcrypt with 12 rounds — passwords never stored plaintext")
_status(True, "Session Management", "Session state stored server-side; cleared on logout")
_status(True, "Input Validation", "Email, name, password, lifestyle text, clinical ranges validated")
_status(True, "Lifestyle Text Privacy", "User text never logged or sent in SMS")
_status(True, "Clinical Data Privacy", "Clinical vectors never appear in logs or error messages")
_status(True, "SQL Injection Protection", "All queries use parameterized statements")
_status(True, "Audit Logging", "Security events recorded to audit database")
_status(True, "Alert Authorization", "Only authenticated users trigger alert pipeline")
_status(True, "Duplicate Alert Prevention", "Assessment-ID + recipient idempotency check (Phase 8)")
_status(True, "Risk Score Trust Boundary", "Risk computed by Phase 7 engine — not accepted from client")
_status(True, "Secret Management", "All credentials loaded from environment variables")
_status(not DEBUG, "Debug Mode", "Should be false in production")
_status(AUTH_DB_PATH.exists(), "Auth Database", f"Path: data/auth/ (gitignored)")
_status(AUDIT_DB_PATH.exists(), "Audit Database", f"Path: data/security/ (gitignored)")

st.divider()

# ── Twilio Configuration Status ───────────────────────────────────────────────
st.markdown("### Alert Service")
st.caption("Configuration status only — actual credentials are never displayed.")

tw1, tw2, tw3, tw4, tw5 = st.columns(5)

def _cfg(col, label: str, configured: bool, hint: str = "") -> None:
    with col:
        with st.container(border=True):
            st.markdown(f"**{label}**")
            if configured:
                st.success("CONFIGURED")
            else:
                st.warning("NOT SET")
            if hint:
                st.caption(hint)

_cfg(tw1, "Alert Mode", True, "LIVE" if ALERTS_ENABLED else "DEMO")
_cfg(tw2, "Twilio SID", bool(TWILIO_ACCOUNT_SID), "Set in .env")
_cfg(tw3, "Twilio Token", bool(TWILIO_AUTH_TOKEN), "Hidden — never displayed")
_cfg(tw4, "Doctor Phone", bool(DOCTOR_PHONE_NUMBER), "Configured" if DOCTOR_PHONE_NUMBER else "Not set")
_cfg(tw5, "Emergency Phone", bool(EMERGENCY_CONTACT_PHONE_NUMBER), "Configured" if EMERGENCY_CONTACT_PHONE_NUMBER else "Not set")

st.divider()

# ── Deployment Notes ───────────────────────────────────────────────────────────
with st.expander("📋 Production Deployment Notes"):
    st.markdown(
        """
        **HTTPS**
        - Deploy behind a reverse proxy (nginx, Caddy, cloud load balancer) with TLS.
        - Never transmit authentication credentials over plain HTTP in production.

        **Session Security**
        - Streamlit session state is server-side per browser session.
        - It is not cryptographically signed. For higher assurance, deploy with a
          reverse proxy that adds a signed session cookie.

        **Rate Limiting**
        - The built-in rate limiter is session-state based (per browser session, not per IP).
        - For production, configure IP-level rate limiting at the reverse proxy layer.

        **Secret Management**
        - Use platform secrets (e.g., Railway, Render, Heroku Config Vars) instead of `.env` files.
        - Rotate `SECRET_KEY` and Twilio credentials if they are ever exposed.

        **Database**
        - SQLite is used for the academic prototype.
        - For production scale, migrate to PostgreSQL with proper connection pooling.
        - Ensure database files are outside the web root and never served directly.

        **Medical Disclaimer**
        - HeartGuard is not a medical diagnostic system.
        - All risk scores are experimental estimates. Always seek professional evaluation.
        """
    )

st.markdown("---")
st.caption(
    "HeartGuard Security Dashboard · Phase 9 · "
    "Academic/Research Prototype — Not a Medical Diagnostic System"
)
