"""Admin Analytics Dashboard for HeartGuard (Phase 17).

Comprehensive system-level analytics dashboard for administrators.
Sections: Users, Assessments, Predictions, Risk Distribution, Alerts,
Recommendations, Reports, System Health, and Monitoring Events.
"""

from __future__ import annotations

import streamlit as st

from config.settings import PROJECT_NAME
from src.auth.authorization import require_role
from src.auth.session_manager import get_current_user, clear_session
from src.security.audit_logger import log_event
from src.analytics.analytics_service import AnalyticsService
from src.analytics.prediction_analytics import PredictionAnalytics
from src.analytics.risk_analytics import RiskAnalytics
from src.analytics.alert_analytics import AlertAnalytics
from src.analytics.recommendation_analytics import RecommendationAnalytics
from src.analytics.explainability_analytics import ExplainabilityAnalytics
from src.analytics.security_analytics import SecurityAnalytics
from src.analytics.anomaly_detection import AnomalyDetector
from src.analytics.monitoring_events import MonitoringEventService
from src.analytics.performance_monitoring import PerformanceMonitor
from src.ui import (
    prepare_category_distribution_chart,
    prepare_alert_distribution_chart,
    render_chart,
)

st.set_page_config(page_title=f"{PROJECT_NAME} — Analytics Dashboard", layout="wide")

require_role("ADMIN")
current_user = get_current_user()
log_event("admin_access", "SUCCESS", user_id=current_user["id"], role=current_user["role"],
          detail="Analytics dashboard accessed")

# Sidebar
with st.sidebar:
    st.markdown(f"**{current_user['name']}**")
    st.caption(f"Role: `{current_user['role']}`")
    st.divider()
    st.page_link("pages/dashboard.py", label="📊 Patient Dashboard")
    st.page_link("pages/admin.py", label="🛡️ Admin Dashboard")
    st.page_link("pages/analytics_dashboard.py", label="📈 Analytics Dashboard")
    st.page_link("pages/model_monitoring.py", label="🔬 Model Monitoring")
    st.page_link("pages/security.py", label="🔐 Security & Audit Log")
    st.divider()
    if st.button("🚪 Log Out", use_container_width=True, key="analytics_admin_logout"):
        log_event("logout", "SUCCESS", user_id=current_user["id"], role=current_user["role"])
        clear_session()
        st.switch_page("pages/login.py")

# Header
st.title("📈 System Analytics Dashboard")
st.caption(f"Logged in as **{current_user['name']}** · Role: `{current_user['role']}`")

# Time filter
time_filter = st.selectbox(
    "Time Range",
    options=["all", "7d", "30d", "90d"],
    index=0,
    format_func=lambda x: {"all": "All Time", "7d": "Last 7 Days", "30d": "Last 30 Days", "90d": "Last 90 Days"}.get(x, x),
    key="admin_time_filter",
)
st.divider()

# ── Assessment Overview ──────────────────────────────────────────────────────
st.markdown("### 📊 Assessment Overview")
try:
    pred_summary = PredictionAnalytics.get_prediction_summary(
        date_range=time_filter if time_filter != "all" else None
    )
    o1, o2, o3, o4, o5 = st.columns(5)
    with o1:
        st.metric("Total Predictions", pred_summary["total_predictions"])
    with o2:
        st.metric("Unique Patients", pred_summary["unique_patients"])
    with o3:
        avg_risk = pred_summary.get("risk_statistics", {}).get("mean", 0)
        st.metric("Mean Risk", f"{avg_risk:.1f}%")
    with o4:
        total_alerts = sum(pred_summary.get("alert_status_distribution", {}).values())
        st.metric("Total Alerts", total_alerts)
    with o5:
        n_versions = len(pred_summary.get("model_version_distribution", {}))
        st.metric("Model Versions", n_versions)
except Exception as exc:
    st.warning(f"Unable to load assessment overview: {exc}")

st.divider()

# ── Risk Distribution ────────────────────────────────────────────────────────
st.markdown("### 📊 Risk Distribution")
try:
    risk_dist = RiskAnalytics.get_risk_distribution(
        date_range=time_filter if time_filter != "all" else None
    )
    if risk_dist["total"] > 0:
        r1, r2 = st.columns(2)
        with r1:
            cat_chart = prepare_category_distribution_chart(
                {k: v["count"] for k, v in risk_dist["categories"].items()}
            )
            if cat_chart:
                render_chart(cat_chart)
        with r2:
            import pandas as pd
            df = pd.DataFrame([
                {"Category": k, "Count": v["count"], "Avg Risk": f"{v['avg_risk']:.1f}%", "Percentage": f"{v['percentage']:.1f}%"}
                for k, v in risk_dist["categories"].items()
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No assessment data available for risk distribution.")
except Exception as exc:
    st.warning(f"Unable to load risk distribution: {exc}")

st.divider()

# ── Prediction Trend ─────────────────────────────────────────────────────────
st.markdown("### 📈 Prediction Trend")
try:
    trend = PredictionAnalytics.get_prediction_trend(
        interval="daily",
        date_range=time_filter if time_filter != "all" else None,
    )
    if trend:
        import pandas as pd
        import altair as alt
        df = pd.DataFrame(trend)
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("period:T", title="Date"),
            y=alt.Y("prediction_count:Q", title="Predictions"),
            tooltip=["period", "prediction_count", "avg_risk"],
        ).properties(title="Daily Prediction Volume", height=250)
        render_chart(chart)
    else:
        st.info("No trend data available.")
except Exception as exc:
    st.warning(f"Unable to load prediction trend: {exc}")

st.divider()

# ── Model Version Analytics ──────────────────────────────────────────────────
st.markdown("### 🤖 Model Version Analytics")
try:
    model_versions = PredictionAnalytics.get_model_version_analytics()
    if model_versions:
        import pandas as pd
        df = pd.DataFrame(model_versions)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No model version data available.")
except Exception as exc:
    st.warning(f"Unable to load model version analytics: {exc}")

st.divider()

# ── Alert Analytics ──────────────────────────────────────────────────────────
st.markdown("### 🚨 Alert Analytics")
try:
    alert_summary = AlertAnalytics.get_alert_summary(
        date_range=time_filter if time_filter != "all" else None
    )
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("Total Alerts", alert_summary["total_alerts"])
    with a2:
        success = alert_summary["by_status"].get("SUCCESS", 0)
        st.metric("Successful", success)
    with a3:
        failed = alert_summary["by_status"].get("FAILED", 0)
        st.metric("Failed", failed)
    with a4:
        rate = AlertAnalytics.get_alert_success_rate(
            date_range=time_filter if time_filter != "all" else None
        )
        sr = rate.get("success_rate")
        st.metric("Success Rate", f"{sr:.1%}" if sr is not None else "N/A")

    if alert_summary["by_risk_level"]:
        alert_chart = prepare_alert_distribution_chart(alert_summary["by_risk_level"])
        if alert_chart:
            render_chart(alert_chart)
except Exception as exc:
    st.warning(f"Unable to load alert analytics: {exc}")

st.divider()

# ── Recommendation Analytics ─────────────────────────────────────────────────
st.markdown("### 💡 Recommendation Analytics")
try:
    rec_summary = RecommendationAnalytics.get_recommendation_summary(
        date_range=time_filter if time_filter != "all" else None
    )
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.metric("Total Recommendations", rec_summary["total_recommendations"])
    with rc2:
        st.metric("Unique Users", rec_summary["unique_users"])
    with rc3:
        avg = RecommendationAnalytics.get_average_recommendations_per_assessment(
            date_range=time_filter if time_filter != "all" else None
        )
        st.metric("Avg per Assessment", f"{avg['avg_per_assessment']:.1f}")

    if rec_summary["by_category"]:
        import pandas as pd
        st.markdown("#### By Category")
        df = pd.DataFrame(list(rec_summary["by_category"].items()), columns=["Category", "Count"])
        st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as exc:
    st.warning(f"Unable to load recommendation analytics: {exc}")

st.divider()

# ── Explainability Analytics ─────────────────────────────────────────────────
st.markdown("### 🧬 Explainability Analytics")
try:
    shap_summary = ExplainabilityAnalytics.get_feature_importance_summary(
        date_range=time_filter if time_filter != "all" else None
    )
    st.caption(shap_summary.get("privacy_note", ""))
    if shap_summary.get("top_features"):
        import pandas as pd
        df = pd.DataFrame(shap_summary["top_features"])
        st.dataframe(df[["feature", "frequency", "frequency_pct", "avg_abs_shap"]].rename(
            columns={"feature": "Feature", "frequency": "Frequency", "frequency_pct": "Freq %", "avg_abs_shap": "Avg |SHAP|"}
        ), use_container_width=True, hide_index=True)
    else:
        st.info(shap_summary.get("message", "No explainability data available."))
except Exception as exc:
    st.warning(f"Unable to load explainability analytics: {exc}")

st.divider()

# ── Security Analytics ───────────────────────────────────────────────────────
st.markdown("### 🔐 Security Analytics")
try:
    sec_summary = SecurityAnalytics.get_security_summary(
        date_range=time_filter if time_filter != "all" else None
    )
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Total Events", sec_summary["total_events"])
    with s2:
        st.metric("Failed Logins", sec_summary["failed_logins"])
    with s3:
        st.metric("Auth Failures", sec_summary["authorization_failures"])
    with s4:
        st.metric("Admin Actions", sec_summary["admin_actions"])
except Exception as exc:
    st.warning(f"Unable to load security analytics: {exc}")

st.divider()

# ── Anomaly Detection ────────────────────────────────────────────────────────
st.markdown("### 🔍 Anomaly Detection")
try:
    anomaly_results = AnomalyDetector.run_comprehensive_anomaly_detection()
    ad1, ad2 = st.columns(2)
    with ad1:
        vol = anomaly_results["checks"].get("assessment_volume", {})
        status_color = "success" if vol.get("status") == "HEALTHY" else "warning"
        getattr(st, status_color)(f"Assessment Volume: {vol.get('status', 'UNKNOWN')}")
    with ad2:
        pred = anomaly_results["checks"].get("prediction_distribution", {})
        status_color = "success" if pred.get("status") == "HEALTHY" else "warning"
        getattr(st, status_color)(f"Prediction Distribution: {pred.get('status', 'UNKNOWN')}")
except Exception as exc:
    st.warning(f"Unable to run anomaly detection: {exc}")

st.divider()

# ── Monitoring Events ────────────────────────────────────────────────────────
st.markdown("### 📋 Recent Monitoring Events")
try:
    events = MonitoringEventService.get_recent_events(limit=15)
    if events:
        import pandas as pd
        df = pd.DataFrame(events)
        display_cols = ["timestamp", "event_type", "severity", "component", "status", "message"]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], use_container_width=True, hide_index=True)
    else:
        st.info("No monitoring events recorded yet.")
except Exception as exc:
    st.warning(f"Unable to load monitoring events: {exc}")

st.divider()

# ── Medical Disclaimer ──────────────────────────────────────────────────────
st.markdown(
    "> **Disclaimer:** Analytics are aggregated, statistical summaries. "
    "Engineering monitoring thresholds are NOT clinical thresholds. "
    "Drift warnings indicate data distribution differences, not medical safety determinations."
)
