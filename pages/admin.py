"""Admin Dashboard page for HeartGuard (Phase 9).

ADMIN role required. Shows system status, service health, user statistics,
and recent audit log. Never displays: Twilio auth token, password hashes,
raw patient medical data, or environment secrets.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from config.settings import (
    ALERTS_ENABLED,
    DEMO_MODE,
    MODEL_DIRECTORY,
    REPORT_DIRECTORY,
    TWILIO_ACCOUNT_SID,
    TWILIO_PHONE_NUMBER,
)
from src.auth.authorization import require_role
from src.auth.session_manager import get_current_user
from src.auth.user_repository import count_users_by_role, list_users
from src.security.audit_logger import get_recent_events, log_event
from src.ui import render_sidebar, inject_global_theme

st.set_page_config(page_title="HeartGuard Admin", layout="wide")

# ── Authorization ───────────────────────────────────────────────────────────
require_role("ADMIN")
current_user = get_current_user()
log_event(
    event_type="admin_access",
    status="SUCCESS",
    user_id=current_user["id"],
    role=current_user["role"],
    detail="Admin dashboard accessed",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
inject_global_theme()
render_sidebar()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🛡️ Admin Dashboard")
st.caption(f"Logged in as **{current_user['name']}** · Role: `{current_user['role']}`")
st.divider()

# ── System Status ────────────────────────────────────────────────────────────
st.markdown("### System Status")

best_model_path = REPORT_DIRECTORY / "best_model.json"
preprocessor_path = MODEL_DIRECTORY / "preprocessor.pkl"

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.markdown("**ML Model**")
        if best_model_path.exists() and preprocessor_path.exists():
            st.success("READY")
            try:
                info = json.loads(best_model_path.read_text())
                st.caption(info.get("model_name", "unknown"))
            except Exception:
                st.caption("Loaded")
        else:
            st.warning("NOT TRAINED")
            st.caption("Run scripts/train_models.py")

with col2:
    with st.container(border=True):
        st.markdown("**SHAP Explainability**")
        if best_model_path.exists():
            st.success("READY")
            st.caption("TreeExplainer / LinearExplainer")
        else:
            st.info("REQUIRES MODEL")

with col3:
    with st.container(border=True):
        st.markdown("**Lifestyle NLP**")
        st.success("READY")
        st.caption("Rule-Based Lexicon")

with col4:
    with st.container(border=True):
        st.markdown("**Multimodal Engine**")
        if best_model_path.exists():
            st.success("READY")
            st.caption("70% Clinical + 30% Lifestyle")
        else:
            st.warning("REQUIRES MODEL")

st.divider()

# ── Alert / Twilio Status ────────────────────────────────────────────────────
st.markdown("### Alert Service Configuration")

a1, a2, a3, a4 = st.columns(4)

with a1:
    with st.container(border=True):
        st.markdown("**Alert Mode**")
        if ALERTS_ENABLED:
            st.success("LIVE MODE")
            st.caption("SMS alerts enabled")
        else:
            st.info("DEMO MODE")
            st.caption("External SMS disabled")

with a2:
    with st.container(border=True):
        st.markdown("**Twilio Account**")
        if TWILIO_ACCOUNT_SID:
            st.success("CONFIGURED")
            # Show only first 6 chars of SID — never the auth token
            st.caption(f"SID: {TWILIO_ACCOUNT_SID[:6]}…")
        else:
            st.warning("NOT CONFIGURED")

with a3:
    with st.container(border=True):
        st.markdown("**Twilio Auth Token**")
        # NEVER display the actual token — only show configured/not
        if st.session_state.get("_show_token_warning"):
            st.warning("CONFIGURED (hidden)")
        else:
            from config.settings import TWILIO_AUTH_TOKEN
            if TWILIO_AUTH_TOKEN:
                st.success("CONFIGURED")
                st.caption("Value hidden for security")
            else:
                st.warning("NOT CONFIGURED")

with a4:
    with st.container(border=True):
        st.markdown("**Twilio Phone**")
        if TWILIO_PHONE_NUMBER:
            st.success("CONFIGURED")
            # Show only last 4 digits
            masked = "***" + TWILIO_PHONE_NUMBER[-4:] if len(TWILIO_PHONE_NUMBER) >= 4 else "***"
            st.caption(f"Number: {masked}")
        else:
            st.warning("NOT CONFIGURED")

st.divider()

from src.ui import (
    prepare_alert_distribution_chart,
    prepare_category_distribution_chart,
    prepare_review_distribution_chart,
    render_chart,
)

# ── User Statistics ───────────────────────────────────────────────────────────
st.markdown("### User Statistics")

try:
    role_counts = count_users_by_role()
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        st.metric("Patient Accounts", role_counts.get("PATIENT", 0))
    with u2:
        st.metric("Reviewer Accounts", role_counts.get("REVIEWER", 0))
    with u3:
        st.metric("Admin Accounts", role_counts.get("ADMIN", 0))
    with u4:
        total = sum(role_counts.values())
        st.metric("Total Active Users", total)
except Exception:
    st.warning("Unable to load user statistics.")

st.divider()

# ── System Assessment Analytics (Phase 12) ──────────────────────────────────
st.markdown("### 📊 System Assessment & Review Analytics")
st.caption("Aggregated platform metrics. Individual patient medical data and lifestyle narratives are never exposed.")

try:
    from src.analytics.analytics_service import AnalyticsService
    import pandas as pd
    sys_stats = AnalyticsService.get_admin_aggregated_analytics()
    rev_stats = sys_stats.get("review_statistics", {})

    sa1, sa2, sa3, sa4, sa5 = st.columns(5)
    with sa1:
        st.metric("Total Assessments", sys_stats["total_assessments"])
    with sa2:
        st.metric("Assessed Patients", sys_stats["active_patients"])
    with sa3:
        st.metric("System Mean Risk", f"{sys_stats['average_system_risk']:.1f}%")
    with sa4:
        st.metric("Total Reviews", rev_stats.get("total_reviews", 0))
    with sa5:
        pending_total = rev_stats.get("pending", 0) + rev_stats.get("unassigned_pending", 0)
        st.metric("Pending Reviews", pending_total)

    if sys_stats["total_assessments"] > 0 or rev_stats.get("total_reviews", 0) > 0:
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            cat_chart = prepare_category_distribution_chart(sys_stats.get("category_distribution", {}))
            if cat_chart is not None:
                render_chart(cat_chart)
            else:
                st.markdown("#### Risk Category Distribution")
                st.dataframe(
                    pd.DataFrame(list(sys_stats["category_distribution"].items()), columns=["Category", "Count"]),
                    use_container_width=True,
                    hide_index=True,
                )
        with c_col2:
            rev_dist = sys_stats.get("review_distribution", {})
            rev_chart = prepare_review_distribution_chart(rev_dist)
            if rev_chart is not None:
                render_chart(rev_chart)
            else:
                st.markdown("#### Review Distribution")
                st.dataframe(
                    pd.DataFrame(list(rev_dist.items()), columns=["Status", "Count"]),
                    use_container_width=True,
                    hide_index=True,
                )

        c_col3, c_col4 = st.columns(2)
        with c_col3:
            alert_dist = sys_stats.get("alert_status_distribution", {})
            alert_chart = prepare_alert_distribution_chart(alert_dist)
            if alert_chart is not None:
                render_chart(alert_chart)
            else:
                st.markdown("#### Alert Dispatch Statistics")
                st.dataframe(
                    pd.DataFrame(list(alert_dist.items()), columns=["Outcome", "Count"]),
                    use_container_width=True,
                    hide_index=True,
                )
        with c_col4:
            st.markdown("#### Model Version Usage")
            st.dataframe(
                pd.DataFrame(list(sys_stats["model_version_distribution"].items()), columns=["Model Version", "Usage Count"]),
                use_container_width=True,
                hide_index=True,
            )
except Exception as exc:
    st.warning(f"Unable to load assessment analytics: {exc}")

st.divider()

# ── User List ─────────────────────────────────────────────────────────────────
with st.expander("👥 User Accounts (Admin View)"):
    st.caption(
        "Displaying: name, email, role, status, created date. "
        "Password hashes are never shown."
    )
    try:
        users = list_users()
        if users:
            import pandas as pd
            rows = [
                {
                    "Name": u.name,
                    "Email": u.email,
                    "Role": u.role,
                    "Active": "✅" if u.is_active else "❌",
                    "Created": u.created_at[:10],
                }
                for u in users
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No users registered yet.")
    except Exception:
        st.warning("Unable to load user list.")

st.divider()

# ── Audit Log ─────────────────────────────────────────────────────────────────
st.markdown("### Recent Security Events")
st.caption("Last 50 audit log entries. Sensitive values (passwords, tokens, clinical data) are never stored here.")

try:
    events = get_recent_events(limit=50)
    if events:
        import pandas as pd
        df = pd.DataFrame(events)[
            ["timestamp", "event_type", "user_id", "role", "status", "detail"]
        ]
        df.columns = ["Timestamp", "Event", "User ID", "Role", "Status", "Detail"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No audit events recorded yet.")
except Exception:
    st.warning("Unable to load audit log.")
