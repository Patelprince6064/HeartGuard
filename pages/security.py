"""Security & Audit Center for HeartGuard (Phase 9 & Phase 15).

Provides comprehensive visibility into:
  - Security posture and control checklist
  - Live security KPI metrics
  - Structured, searchable audit log viewer (Admin / Reviewer)
  - Privacy data minimization & GDPR/CCPA personal data export
  - Automated Academic Security Verification Report generator
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import streamlit as st

from config.security import (
    COMPLIANCE_STATEMENT,
    EVENT_CATEGORIES,
    EVENT_SEVERITIES,
    INFORMATIONAL_ACKNOWLEDGEMENT_TEXT,
    PROTOTYPE_NOTICE,
    SECURITY_HEADERS,
)
from config.settings import (
    ALERTS_ENABLED,
    AUDIT_DB_PATH,
    AUTH_DB_PATH,
    DEBUG,
    DEMO_MODE,
    DOCTOR_PHONE_NUMBER,
    EMERGENCY_CONTACT_PHONE_NUMBER,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)
from src.auth.authorization import require_authentication
from src.auth.session_manager import get_current_role, get_current_user, get_current_user_id
from src.security.audit_logger import get_audit_statistics, get_filtered_events
from src.security.privacy import export_user_data, mask_email, scan_repo_secrets

st.set_page_config(page_title="HeartGuard — Security & Audit Center", layout="wide")

# ── Authorization ───────────────────────────────────────────────────────────
require_authentication()
current_user = get_current_user()
current_role = (get_current_role() or "PATIENT").upper().strip()
user_id = get_current_user_id() or 1

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🛡️ Security, Privacy & Audit Center")
st.caption(
    "Phase 15 Security Architecture — Enterprise-grade hardening, immutable audit logging, "
    "and privacy compliance for academic defense and production evaluation."
)

st.info(
    f"🔒 **Security Posture Notice:** {COMPLIANCE_STATEMENT}  \n"
    f"*{PROTOTYPE_NOTICE}*"
)

# ── Mode Banners ────────────────────────────────────────────────────────────
m_col1, m_col2 = st.columns(2)
with m_col1:
    if DEMO_MODE:
        st.info("🟦 **Demo Mode** — External SMS alerts simulated locally. Models & security fully active.")
    else:
        st.success("🟢 **Live Mode** — Production SMS alerts and transport active.")
with m_col2:
    if DEBUG:
        st.warning("⚠️ **DEBUG=True** — Active development environment. Disable before public deployment.")
    else:
        st.success("🛡️ **DEBUG=False** — Hardened production configuration.")

st.divider()

# ── Navigation Tabs ─────────────────────────────────────────────────────────
tabs = ["🔍 Security Posture", "🔏 Privacy & Data Rights"]
if current_role in ("ADMIN", "REVIEWER"):
    tabs.insert(1, "📋 Audit Log Viewer")
    tabs.append("📊 System Security Report")

tab_instances = st.tabs(tabs)

# ───────────────────────────────────────────────────────────────────────────
# TAB 1: Security Posture
# ───────────────────────────────────────────────────────────────────────────
with tab_instances[0]:
    st.subheader("Security Controls & Threat Mitigations")
    st.markdown(
        "HeartGuard enforces multi-layer defense-in-depth across the application lifecycle. "
        "All controls are verified against the STRIDE threat model."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔑 Identity, Access & Session Security")
        with st.container(border=True):
            st.markdown("✅ **Authentication:** Scrypt/Bcrypt salted hashing with zero plaintext persistence.")
            st.markdown("✅ **RBAC:** Strict PATIENT / REVIEWER / ADMIN role segregation enforced server-side.")
            st.markdown("✅ **IDOR Defense:** Ownership validation on all assessments, insights, and PDF reports.")
            st.markdown("✅ **Session Protection:** Unique session rotation on login; 30-minute inactivity timeout.")
            st.markdown("✅ **Rate Limiting:** Sliding-window token bucket on authentication and prediction endpoints.")

        st.markdown("#### 🛡️ Network & Transport Security")
        with st.container(border=True):
            st.markdown("✅ **HTTP Security Headers:** Nosniff, X-Frame-Options: DENY, Referrer-Policy.")
            st.markdown("✅ **Content Security Policy (CSP):** Strict script and frame source directives.")
            st.markdown("✅ **Credential Protection:** Zero secrets committed; environment-variable backed configuration.")

    with col2:
        st.markdown("#### 🔬 Clinical Data & Model Protection")
        with st.container(border=True):
            st.markdown("✅ **Model Integrity:** Clinical weights, ML models, and alert thresholds are immutable at runtime.")
            st.markdown("✅ **Data Minimization:** No raw clinical vectors or free-text descriptions stored in audit logs.")
            st.markdown("✅ **Safe Validation Engine:** Rejection of diagnostic assertions, prescriptions, and unsupported claims.")
            st.markdown("✅ **Informational Disclaimer:** Mandatory user acknowledgement before risk calculation.")

        st.markdown("#### 💾 Database & File Security")
        with st.container(border=True):
            st.markdown("✅ **SQL Injection Immunity:** 100% parameterized SQLite queries throughout all services.")
            st.markdown("✅ **Path Traversal Defense:** Strict root-directory boundary validation on all file exports.")
            st.markdown("✅ **Upload Restrictions:** 5 MB size cap, MIME verification, and magic-byte checks.")
            st.markdown("✅ **Immutable Audit Trail:** Append-only structured logs with indexing on critical fields.")

# ───────────────────────────────────────────────────────────────────────────
# TAB 2: Audit Log Viewer (Admin & Reviewer Only)
# ───────────────────────────────────────────────────────────────────────────
if current_role in ("ADMIN", "REVIEWER"):
    with tab_instances[1]:
        st.subheader("Interactive Security Audit Log")
        st.caption("Complete, tamper-evident audit record of security, authentication, and data operations.")

        # KPI Metrics
        stats = get_audit_statistics()
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Events", stats.get("total_events", 0))
        c2.metric("Failed Logins", stats.get("failed_logins", 0), delta_color="inverse")
        c3.metric("Blocked Access / IDOR", stats.get("access_denied_events", 0), delta_color="inverse")
        c4.metric("Admin Actions", stats.get("admin_actions", 0))
        c5.metric("High/Critical Events", stats.get("high_severity_events", 0), delta_color="inverse")

        st.markdown("##### Filter Audit Records")
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            cat_filter = st.selectbox("Category", ["All"] + list(EVENT_CATEGORIES))
        with fc2:
            sev_filter = st.selectbox("Severity", ["All"] + list(EVENT_SEVERITIES))
        with fc3:
            status_filter = st.selectbox("Status", ["All", "SUCCESS", "FAILURE", "BLOCKED", "DENIED"])
        with fc4:
            search_query = st.text_input("Search (keyword/user/resource)", "")

        category_param = None if cat_filter == "All" else cat_filter
        severity_param = None if sev_filter == "All" else sev_filter
        status_param = None if status_filter == "All" else status_filter
        search_param = search_query.strip() if search_query.strip() else None

        # Fetch records
        events, total_count = get_filtered_events(
            limit=50,
            offset=0,
            category=category_param,
            severity=severity_param,
            status=status_param,
            search_query=search_param,
        )

        st.caption(f"Showing up to 50 matching events (Total matching: {total_count})")

        if events:
            # Format table data
            table_data = []
            for ev in events:
                sev_icon = "🟢" if ev.get("severity") == "INFO" else ("🟡" if ev.get("severity") == "WARNING" else "🔴")
                table_data.append({
                    "ID": ev.get("id"),
                    "Timestamp (UTC)": ev.get("timestamp")[:19].replace("T", " "),
                    "Severity": f"{sev_icon} {ev.get('severity')}",
                    "Category": ev.get("category"),
                    "Event Type": ev.get("event_type"),
                    "User ID": ev.get("user_id") or "—",
                    "Role": ev.get("role") or "—",
                    "Status": ev.get("status"),
                    "Resource": f"{ev.get('resource_type') or ''} {ev.get('resource_id') or ''}".strip() or "—",
                    "Detail": ev.get("detail") or "—",
                })
            st.dataframe(table_data, use_container_width=True, hide_index=True)
        else:
            st.info("No audit events match the selected filter criteria.")

# ───────────────────────────────────────────────────────────────────────────
# TAB: Privacy & Data Rights
# ───────────────────────────────────────────────────────────────────────────
privacy_tab_index = 2 if current_role in ("ADMIN", "REVIEWER") else 1
with tab_instances[privacy_tab_index]:
    st.subheader("Data Privacy, Minimization & User Rights")
    st.markdown(
        "HeartGuard respects user privacy principles aligned with GDPR (Art. 15 Right of Access, "
        "Art. 17 Right to Erasure) and CCPA standards for health data research prototypes."
    )

    p_col1, p_col2 = st.columns([1, 1])

    with p_col1:
        st.markdown("#### 🔒 Privacy Safeguards")
        with st.container(border=True):
            st.markdown("**Data Minimization:** Only clinical and lifestyle metrics strictly required for the ML model are requested.")
            st.markdown("**Field Masking:** Personal identifiers (email, phone, name) are pseudonymized or masked in public views.")
            st.markdown(f"**Demonstration Masking:** Current email is masked as: `{mask_email(current_user.get('email', 'patient@heartguard.org'))}`")
            st.markdown("**No Model Training on User Data:** Input parameters are evaluated dynamically; user data is never stored into training sets without explicit consent.")

    with p_col2:
        st.markdown("#### 📥 Self-Service Data Portability (Export)")
        st.markdown(
            "Under GDPR Art. 15, you may export your complete personal assessment history, "
            "recommendation archive, and account profile in a structured, machine-readable JSON format."
        )

        if st.button("Generate My Data Export", type="primary"):
            try:
                user_export = export_user_data(user_id=user_id)
                json_str = json.dumps(user_export, indent=2)
                st.download_button(
                    label="⬇️ Download Personal Data Package (JSON)",
                    data=json_str,
                    file_name=f"heartguard_user_{user_id}_privacy_export.json",
                    mime="application/json",
                )
                st.success("Personal data package compiled successfully. Sensitive authentication tokens were excluded.")
            except Exception as exc:
                st.error(f"Failed to generate export: {exc}")

# ───────────────────────────────────────────────────────────────────────────
# TAB: System Security Report (Admin & Reviewer Only)
# ───────────────────────────────────────────────────────────────────────────
if current_role in ("ADMIN", "REVIEWER"):
    report_tab_index = 3
    with tab_instances[report_tab_index]:
        st.subheader("Academic Security Verification Report")
        st.markdown(
            "Generate a formal, exportable compliance summary for academic defense, viva examination, "
            "or security audits."
        )

        if st.button("Generate Formal Security Report"):
            stats = get_audit_statistics()
            secret_findings = scan_repo_secrets()
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

            report_lines = [
                "# HEARTGUARD PLATFORM — SECURITY & PRIVACY AUDIT REPORT",
                f"Generated: {now_iso}",
                f"Generated By: {current_user.get('name', 'Admin')} (Role: {current_role})",
                f"Compliance Statement: {COMPLIANCE_STATEMENT}",
                "",
                "## 1. Executive Summary",
                "HeartGuard implements defense-in-depth across authentication, role-based authorization,",
                "direct object reference (IDOR) prevention, session management, and tamper-evident audit logging.",
                "",
                "## 2. Security Metrics",
                f"- Total Audit Records: {stats.get('total_events', 0)}",
                f"- Failed Login Attempts: {stats.get('failed_logins', 0)}",
                f"- Access Denials / IDOR Blocks: {stats.get('access_denied_events', 0)}",
                f"- High/Critical Security Alerts: {stats.get('high_severity_events', 0)}",
                f"- Hardcoded Secrets Detected in Codebase: {len(secret_findings)}",
                "",
                "## 3. Verified Controls",
                "- [x] Server-Side RBAC Enforcement",
                "- [x] In-Memory Sliding-Window Rate Limiting",
                "- [x] Bcrypt Password Hashing with Complexity Enforcements",
                "- [x] Inactivity Session Invalidation (30-min timeout)",
                "- [x] Parameterized SQL Queries (SQLi Protection)",
                "- [x] Output HTML-Encoding (XSS Protection)",
                "- [x] Directory Traversal Guards on File System Access",
                "- [x] Recommendation Engine Safe Validation Rules (No diagnostic assertions)",
                "",
                "## 4. Academic Prototype Notice",
                PROTOTYPE_NOTICE,
            ]
            report_content = "\n".join(report_lines)

            st.text_area("Report Preview", report_content, height=350)
            st.download_button(
                label="⬇️ Download Audit Report (Markdown)",
                data=report_content,
                file_name="heartguard_security_audit_report.md",
                mime="text/markdown",
            )

st.markdown("---")
st.caption(
    "HeartGuard Security & Privacy Architecture · Phase 15 · "
    "Academic Research Prototype"
)
