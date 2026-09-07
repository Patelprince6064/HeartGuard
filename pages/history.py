"""Assessment History, Analytics, and Report Generation Page for HeartGuard (Phase 10).

Allows authenticated patients to view their personal assessment history,
analyze chronological risk trends, compare pairwise evaluations,
and download professional PDF risk assessment reports.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analytics.analytics_service import AnalyticsService
from src.analytics.history_service import HistoryService
from src.analytics.trend_service import TrendService
from src.auth.authorization import require_authentication
from src.auth.session_manager import clear_session, get_current_user
from src.reports.report_generator import ReportGenerator
from src.reports.report_utils import export_assessments_to_csv, sanitize_report_filename
from src.security.audit_logger import log_event
from src.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="HeartGuard Assessment History", layout="wide")

# ── Authorization ────────────────────────────────────────────────────────────
require_authentication()
current_user = get_current_user()
user_id = current_user["id"]

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**{current_user['name']}**")
    st.caption(f"Role: `{current_user['role']}`")
    st.divider()
    if st.button("🚪 Log Out", use_container_width=True, key="history_logout"):
        log_event("logout", "SUCCESS", user_id=user_id, role=current_user["role"])
        clear_session()
        st.switch_page("pages/login.py")

# ── Header ──────────────────────────────────────────────────────────────────
st.title("📜 Assessment History & Analytics")
st.caption(
    "Your assessment history is private and is available only to your authenticated "
    "account according to the application's access-control policy."
)

st.divider()

# ── Load User Analytics & History ───────────────────────────────────────────
stats = AnalyticsService.calculate_user_statistics(user_id=user_id)
total_count = stats["total_assessments"]

# ── High-Level Metrics ───────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("Total Assessments", total_count)
with m2:
    latest_val = f"{stats['latest_risk']:.1f}%" if stats["latest_risk"] is not None else "N/A"
    st.metric("Latest Risk", latest_val)
with m3:
    latest_cat = stats["latest_category"] or "N/A"
    st.metric("Latest Category", latest_cat)
with m4:
    st.metric("Critical Assessments", stats["critical_count"])
with m5:
    avg_val = f"{stats['average_overall_risk']:.1f}%" if stats["average_overall_risk"] is not None else "N/A"
    st.metric("Average Model Risk", avg_val)

st.divider()

# ── Empty State ──────────────────────────────────────────────────────────────
if total_count == 0:
    st.info("### ℹ️ No assessment history available.")
    st.markdown(
        "You have not completed any cardiovascular risk assessments yet. "
        "Complete your first assessment to begin tracking your risk trajectory and generating reports."
    )
    st.page_link("pages/risk_assessment.py", label="🩺 Start New Assessment →")
    st.stop()

# ── Latest Assessment & Comparison ──────────────────────────────────────────
latest_assessment = HistoryService.get_latest_assessment(user_id=user_id)
previous_assessment = HistoryService.get_previous_assessment(user_id=user_id)
comparison = TrendService.compare_assessments(latest_assessment, previous_assessment)

col_latest, col_comp = st.columns([1, 1])

with col_latest:
    with st.container(border=True):
        st.markdown("### 📌 Latest Assessment")
        if latest_assessment:
            st.markdown(f"**Date:** `{latest_assessment.created_at[:10]}` · **ID:** `{latest_assessment.assessment_id}`")
            st.markdown(f"**Overall Risk:** `{latest_assessment.overall_risk:.1f}%` ({latest_assessment.risk_category})")
            st.markdown(f"**Recommendation:** {latest_assessment.recommendation}")
            st.caption(f"Alert Status: `{latest_assessment.alert_status}` · Model: {latest_assessment.model_version}")

with col_comp:
    with st.container(border=True):
        st.markdown("### 🔄 Latest vs Previous Comparison")
        if comparison:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(
                    "Overall Risk",
                    f"{comparison['overall_risk']['latest']:.1f}%",
                    delta=comparison["overall_risk"]["delta_str"],
                )
            with c2:
                st.metric(
                    "Clinical (70%)",
                    f"{comparison['clinical_risk']['latest']:.1f}%",
                    delta=comparison["clinical_risk"]["delta_str"],
                )
            with c3:
                st.metric(
                    "Lifestyle (30%)",
                    f"{comparison['lifestyle_risk']['latest']:.1f}%",
                    delta=comparison["lifestyle_risk"]["delta_str"],
                )

            st.info(f"**Trend:** {comparison['interpretation']}")
            st.caption(comparison["disclaimer"])
        else:
            st.info("Single assessment record available. Comparative analysis will appear once you complete a second assessment.")

st.divider()

# ── Trend Trajectory Charts ─────────────────────────────────────────────────
st.markdown("### 📈 Longitudinal Risk Trends")

trends = TrendService.get_risk_trends(user_id=user_id)
if len(trends) >= 2:
    trend_df = pd.DataFrame(trends)
    trend_df["date"] = pd.to_datetime(trend_df["date"])

    chart_tab1, chart_tab2 = st.tabs(["Overall Risk Trend", "Multimodal Comparison (Clinical vs Lifestyle vs Overall)"])

    with chart_tab1:
        st.caption("Chronological trajectory of overall combined multimodal risk.")
        c_df = trend_df.set_index("date")[["overall_risk"]]
        c_df.columns = ["Overall Risk (%)"]
        st.line_chart(c_df, color="#1e3a8a")

    with chart_tab2:
        st.caption("Component-level comparison across clinical ML, lifestyle NLP, and combined risk.")
        comp_chart_df = trend_df.set_index("date")[["overall_risk", "clinical_risk", "lifestyle_risk"]]
        comp_chart_df.columns = ["Overall Risk (%)", "Clinical Risk (%)", "Lifestyle Risk (%)"]
        st.line_chart(comp_chart_df, color=["#1e3a8a", "#0284c7", "#d97706"])
else:
    st.info("At least two historical assessments are required to plot trend charts.")

# ── Category Distribution ───────────────────────────────────────────────────
st.markdown("### 📊 Risk Category Distribution")
cat_dist = AnalyticsService.get_category_distribution(user_id=user_id)
if cat_dist:
    cat_df = pd.DataFrame(list(cat_dist.items()), columns=["Risk Category", "Assessment Count"]).set_index("Risk Category")
    st.bar_chart(cat_df, color="#0284c7")

st.divider()

# ── History Table with Filters ──────────────────────────────────────────────
st.markdown("### 📋 Historical Assessments")

f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
with f_col1:
    date_filter = st.selectbox("Date Range", options=["All time", "Last 7 days", "Last 30 days", "Last 90 days"])
with f_col2:
    cat_filter = st.selectbox("Filter by Category", options=["All", "CRITICAL", "ELEVATED", "LOWER_RISK"])
with f_col3:
    sort_filter = st.selectbox("Sort Order", options=["Newest First", "Oldest First"])

date_code = None
if date_filter == "Last 7 days":
    date_code = "7d"
elif date_filter == "Last 30 days":
    date_code = "30d"
elif date_filter == "Last 90 days":
    date_code = "90d"

cat_code = None if cat_filter == "All" else cat_filter
sort_dir = "desc" if sort_filter == "Newest First" else "asc"

filtered_assessments = HistoryService.get_user_assessments(
    user_id=user_id,
    date_range=date_code,
    category=cat_code,
    sort_order=sort_dir,
    limit=50,
)

if filtered_assessments:
    table_rows = []
    for a in filtered_assessments:
        table_rows.append(
            {
                "Date": a.created_at[:10],
                "Assessment ID": a.assessment_id,
                "Clinical Risk": f"{a.clinical_risk:.1f}%",
                "Lifestyle Risk": f"{a.lifestyle_risk:.1f}%",
                "Overall Risk": f"{a.overall_risk:.1f}%",
                "Category": a.risk_category,
                "Recommendation": a.recommendation,
                "Alert Status": a.alert_status,
            }
        )
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
else:
    st.info("No assessments found matching the selected filters.")

# CSV Export Button
csv_content = export_assessments_to_csv(user_id=user_id)
st.download_button(
    label="📥 Export Assessment History (CSV)",
    data=csv_content,
    file_name=f"HeartGuard_History_UID_{user_id}.csv",
    mime="text/csv",
    use_container_width=False,
)

st.divider()

# ── Detailed Inspection & PDF Report Generation ─────────────────────────────
st.markdown("### 📄 Assessment Detail & PDF Report Generation")

assessment_options = {
    f"{a.created_at[:10]} — ID: {a.assessment_id} ({a.overall_risk:.1f}% {a.risk_category})": a.assessment_id
    for a in filtered_assessments
}

if assessment_options:
    selected_label = st.selectbox("Select Assessment to Inspect / Generate Report", options=list(assessment_options.keys()))
    selected_id = assessment_options[selected_label]
    selected_assessment = HistoryService.get_assessment_by_id(selected_id, user_id=user_id)

    if selected_assessment:
        with st.expander("🔍 View Assessment Diagnostics & Factors", expanded=True):
            d1, d2, d3, d4 = st.columns(4)
            with d1:
                st.markdown(f"**Overall Risk:** `{selected_assessment.overall_risk:.1f}%`")
            with d2:
                st.markdown(f"**Clinical Risk:** `{selected_assessment.clinical_risk:.1f}%`")
            with d3:
                st.markdown(f"**Lifestyle Risk:** `{selected_assessment.lifestyle_risk:.1f}%`")
            with d4:
                st.markdown(f"**Alert Status:** `{selected_assessment.alert_status}`")

            st.markdown(f"**Model Version:** `{selected_assessment.model_version}`")
            st.markdown(f"**Recommendation:** {selected_assessment.recommendation}")

            # Top SHAP factors if stored
            top_factors = selected_assessment.get_top_clinical_factors()
            if top_factors:
                st.markdown("**Top Clinical Risk Drivers (SHAP):**")
                for tf in top_factors[:5]:
                    lbl = tf.get("clinical_label") or tf.get("feature", "Feature")
                    st.markdown(f"- **{lbl}**: SHAP impact `+{tf.get('shap_value', 0.0):.4f}`")
            else:
                st.caption("Explainability details are available only for assessments where SHAP results were stored.")

        # Report Generation
        r_col1, r_col2 = st.columns([2, 5])
        with r_col1:
            gen_btn = st.button("Generate Assessment Report", type="primary", use_container_width=True)

        report_key = f"_hg_report_pdf_{selected_id}"

        if gen_btn:
            with st.spinner("Generating professional PDF assessment report..."):
                try:
                    pdf_bytes = ReportGenerator.generate_assessment_report(
                        assessment_id=selected_id,
                        user_id=user_id,
                    )
                    st.session_state[report_key] = pdf_bytes
                    st.success("Report Ready!")
                except Exception as exc:
                    logger.error("Report generation failed: %s", type(exc).__name__)
                    st.error("Unable to generate the report. Please try again.")

        if report_key in st.session_state:
            pdf_data = st.session_state[report_key]
            safe_fname = sanitize_report_filename(selected_id)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name=safe_fname,
                mime="application/pdf",
                type="secondary",
            )

st.divider()

# ── Medical & Research Disclaimer ────────────────────────────────────────────
st.markdown(
    "> **Academic & Research Disclaimer:** HeartGuard is an academic/research prototype for "
    "AI-based heart disease risk assessment. It is not a medical diagnostic system and does "
    "not replace evaluation by a qualified healthcare professional. Changes in HeartGuard "
    "risk scores represent changes in the model's assessment inputs and outputs and do not "
    "by themselves establish a medical diagnosis or disease progression."
)
