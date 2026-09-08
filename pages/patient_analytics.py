"""Patient Analytics Page for HeartGuard (Phase 17).

Provides patients with personal analytics: risk trend, assessment history,
risk category distribution, recommendation history, and alert history.
Only shows data belonging to the authenticated patient.
"""

from __future__ import annotations

import streamlit as st

from config.settings import PROJECT_NAME
from src.auth.authorization import require_authentication
from src.auth.session_manager import get_current_user, clear_session
from src.security.audit_logger import log_event
from src.auth.authorization import is_admin, is_reviewer
from src.analytics.analytics_service import AnalyticsService
from src.analytics.history_service import HistoryService
from src.analytics.trend_service import TrendService
from src.analytics.risk_analytics import RiskAnalytics
from src.ui import (
    format_risk_percentage,
    get_alert_status_badge,
    get_risk_category_badge,
    prepare_risk_trend_chart,
    render_chart,
    render_metric_card,
    render_trend_disclaimer,
    safe_render_section,
)

st.set_page_config(
    page_title=f"{PROJECT_NAME} — My Analytics",
    page_icon="📊",
    layout="wide",
)

require_authentication()
current_user = get_current_user()
user_id: int = current_user["id"]

# Sidebar
with st.sidebar:
    st.markdown(f"**{current_user.get('name', 'User')}**")
    st.caption(f"Role: `{current_user['role']}`")
    st.divider()
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/patient_analytics.py", label="📈 My Analytics")
    st.page_link("pages/risk_assessment.py", label="🩺 New Assessment")
    st.page_link("pages/history.py", label="📜 History & Reports")
    if is_reviewer():
        st.page_link("pages/review.py", label="🩺 Doctor Review")
    if is_admin():
        st.page_link("pages/admin.py", label="🛡️ Admin Dashboard")
    st.page_link("pages/security.py", label="🔐 Security & Profile")
    st.divider()
    if st.button("🚪 Log Out", use_container_width=True, key="analytics_logout"):
        log_event("logout", "SUCCESS", user_id=user_id, role=current_user["role"])
        clear_session()
        st.switch_page("pages/login.py")

# Header
st.title("📈 My Analytics")
st.caption("Personal risk analytics and assessment insights.")
st.divider()

# Time filter
filter_col1, filter_col2 = st.columns([1, 3])
with filter_col1:
    time_filter = st.selectbox(
        "Time Range",
        options=["all", "7d", "30d", "90d"],
        index=0,
        format_func=lambda x: {"all": "All Time", "7d": "Last 7 Days", "30d": "Last 30 Days", "90d": "Last 90 Days"}.get(x, x),
        key="patient_time_filter",
    )

# Load data
stats = AnalyticsService.calculate_user_statistics(user_id=user_id)
total_assessments = stats.get("total_assessments", 0)

if total_assessments == 0:
    st.info("📊 No assessment data available yet. Complete a risk assessment to see your personal analytics.")
    st.stop()

# KPI Row
def _render_kpis():
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card(
            title="Total Assessments",
            value=str(total_assessments),
            caption="Completed evaluations",
        )
    with k2:
        latest_risk = stats.get("latest_risk")
        render_metric_card(
            title="Latest Risk",
            value=format_risk_percentage(latest_risk),
            caption="Model-based estimate",
        )
    with k3:
        category = stats.get("latest_category") or "Unknown"
        cat_badge = get_risk_category_badge(category)
        render_metric_card(
            title="Risk Category",
            value=category.upper(),
            badge_md=cat_badge,
            caption="Current tier",
        )
    with k4:
        avg_risk = stats.get("average_overall_risk")
        render_metric_card(
            title="Average Risk",
            value=format_risk_percentage(avg_risk),
            caption="Across all assessments",
        )

safe_render_section("Summary", _render_kpis)
st.divider()

# Risk Trend
def _render_trend():
    st.markdown("### 📈 Model-Based Risk Trend")
    trends = TrendService.get_risk_trends(user_id=user_id)

    if len(trends) < 2:
        st.info("Complete at least two assessments to see your risk trend over time.")
    else:
        chart = prepare_risk_trend_chart(trends)
        if chart is not None:
            render_chart(chart)
    render_trend_disclaimer()

safe_render_section("Risk Trend", _render_trend)
st.divider()

# Risk Category Distribution
def _render_category_dist():
    st.markdown("### 📊 Risk Category Distribution")
    dist = AnalyticsService.get_category_distribution(user_id=user_id)
    if dist:
        import pandas as pd
        df = pd.DataFrame(list(dist.items()), columns=["Category", "Count"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No category data available.")

safe_render_section("Category Distribution", _render_category_dist)
st.divider()

# Risk Statistics
def _render_risk_stats():
    st.markdown("### 📉 Risk Score Statistics")
    risk_stats = RiskAnalytics.get_risk_statistics(date_range=time_filter if time_filter != "all" else None)
    if risk_stats.get("total", 0) > 0:
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("Mean Risk", f"{risk_stats['mean_risk']:.1f}%")
        with s2:
            st.metric("Min Risk", f"{risk_stats['min_risk']:.1f}%")
        with s3:
            st.metric("Max Risk", f"{risk_stats['max_risk']:.1f}%")
        with s4:
            st.metric("Assessments", str(risk_stats["total"]))
    else:
        st.info("Insufficient data for statistics.")

safe_render_section("Risk Statistics", _render_risk_stats)
st.divider()

# Recent Assessments
def _render_recent():
    st.markdown("### 📋 Assessment History")
    assessments = HistoryService.get_user_assessments(
        user_id=user_id,
        date_range=time_filter if time_filter != "all" else None,
        sort_order="desc",
        limit=20,
    )
    if assessments:
        import pandas as pd
        rows = [
            {
                "Date": a.created_at[:10],
                "Risk": f"{a.overall_risk:.1f}%",
                "Category": a.risk_category,
                "Clinical": f"{a.clinical_risk:.1f}%",
                "Lifestyle": f"{a.lifestyle_risk:.1f}%",
                "Alert": a.alert_status,
            }
            for a in assessments
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No assessments found for the selected time range.")

safe_render_section("Assessment History", _render_recent)
st.divider()

# Medical Disclaimer
st.markdown(
    "> **Disclaimer:** These analytics are model-based statistical summaries. "
    "They do not constitute medical diagnosis or disease progression assessment. "
    "Changes in risk scores reflect changes in model inputs and outputs, not "
    "necessarily changes in health status."
)
