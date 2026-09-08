"""Model Monitoring Dashboard for HeartGuard (Phase 17).

Admin-only dashboard for monitoring model performance, data drift,
prediction drift, confidence, data quality, and monitoring events.
"""

from __future__ import annotations

import streamlit as st

from config.settings import PROJECT_NAME
from src.auth.authorization import require_role
from src.auth.session_manager import get_current_user, clear_session
from src.security.audit_logger import log_event
from src.analytics.model_monitoring import ModelMonitoringService
from src.analytics.drift_detection import DriftDetector
from src.analytics.data_quality_monitoring import DataQualityMonitor
from src.analytics.performance_monitoring import PerformanceMonitor
from src.analytics.monitoring_events import MonitoringEventService
from src.analytics.anomaly_detection import AnomalyDetector
from src.ui import render_chart

st.set_page_config(page_title=f"{PROJECT_NAME} — Model Monitoring", layout="wide")

require_role("ADMIN")
current_user = get_current_user()
log_event("admin_access", "SUCCESS", user_id=current_user["id"], role=current_user["role"],
          detail="Model monitoring dashboard accessed")

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
    if st.button("🚪 Log Out", use_container_width=True, key="model_mon_logout"):
        log_event("logout", "SUCCESS", user_id=current_user["id"], role=current_user["role"])
        clear_session()
        st.switch_page("pages/login.py")

st.title("🔬 Model Monitoring Dashboard")
st.caption("Monitor model performance, drift, data quality, and system health.")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 📊 Model Performance")

try:
    status_summary = ModelMonitoringService.get_model_status_summary()
    latest_metrics = ModelMonitoringService.get_latest_metrics()

    # Model status banner
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        best = status_summary.get("best_model", "unknown")
        st.metric("Best Model", best.replace("_", " ").title() if best else "N/A")
    with mc2:
        st.metric("Models Loaded", status_summary.get("total_loaded", 0))
    with mc3:
        integrity = "Verified" if status_summary.get("integrity_verified") else "Unknown"
        st.metric("Integrity", integrity)
    with mc4:
        st.metric("Total Evaluations", len(ModelMonitoringService.get_model_performance_history()))

    if latest_metrics:
        st.markdown("### Latest Evaluation Metrics")
        e1, e2, e3, e4, e5, e6 = st.columns(6)
        with e1:
            val = latest_metrics.get("accuracy")
            st.metric("Accuracy", f"{val:.3f}" if val else "N/A")
        with e2:
            val = latest_metrics.get("precision")
            st.metric("Precision", f"{val:.3f}" if val else "N/A")
        with e3:
            val = latest_metrics.get("recall")
            st.metric("Recall", f"{val:.3f}" if val else "N/A")
        with e4:
            val = latest_metrics.get("f1")
            st.metric("F1", f"{val:.3f}" if val else "N/A")
        with e5:
            val = latest_metrics.get("roc_auc")
            st.metric("ROC-AUC", f"{val:.3f}" if val else "N/A")
        with e6:
            val = latest_metrics.get("pr_auc")
            st.metric("PR-AUC", f"{val:.3f}" if val else "N/A")

    # Model comparison table
    comparison = ModelMonitoringService.get_model_comparison()
    if comparison:
        st.markdown("### Model Comparison")
        import pandas as pd
        df = pd.DataFrame(comparison)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Metric history
    if latest_metrics and latest_metrics.get("model_name"):
        st.markdown("### Metric History")
        metric_options = ["accuracy", "precision", "recall", "f1", "roc_auc"]
        selected_metric = st.selectbox("Select Metric", metric_options, key="metric_hist_select")
        history = ModelMonitoringService.get_metric_history(
            latest_metrics["model_name"], selected_metric
        )
        if history:
            import pandas as pd
            import altair as alt
            df = pd.DataFrame(history)
            chart = alt.Chart(df).mark_line(point=True).encode(
                x=alt.X("evaluation_date:T", title="Evaluation Date"),
                y=alt.Y("value:Q", title=selected_metric.replace("_", " ").title()),
            ).properties(title=f"{selected_metric.replace('_', ' ').title()} Over Time", height=250)
            render_chart(chart)

except Exception as exc:
    st.warning(f"Unable to load model performance: {exc}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# DATA DRIFT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 🔍 Data Drift")

try:
    drift_data = DriftDetector.get_drift_summary_from_assessments()
    if drift_data.get("status") == "INSUFFICIENT_DATA":
        st.info(drift_data.get("message", "Insufficient data for drift analysis."))
    else:
        sample_size = drift_data.get("sample_size", 0)
        st.caption(f"Based on {sample_size} assessment records with clinical data.")

        # Feature drift summary
        numerical = drift_data.get("numerical", {})
        categorical = drift_data.get("categorical", {})

        if numerical or categorical:
            st.markdown("### Current Feature Distributions")
            import pandas as pd

            num_stats = []
            for feat, values in numerical.items():
                if values:
                    import numpy as np
                    arr = np.array(values)
                    num_stats.append({
                        "Feature": feat,
                        "Type": "Numerical",
                        "Count": len(values),
                        "Mean": f"{np.mean(arr):.2f}",
                        "Std": f"{np.std(arr):.2f}",
                        "Min": f"{np.min(arr):.2f}",
                        "Max": f"{np.max(arr):.2f}",
                    })
            if num_stats:
                st.dataframe(pd.DataFrame(num_stats), use_container_width=True, hide_index=True)

            cat_stats = []
            for feat, counts in categorical.items():
                if counts:
                    cat_stats.append({
                        "Feature": feat,
                        "Type": "Categorical",
                        "Categories": len(counts),
                        "Total": sum(counts.values()),
                        "Top Category": max(counts, key=counts.get) if counts else "N/A",
                    })
            if cat_stats:
                st.dataframe(pd.DataFrame(cat_stats), use_container_width=True, hide_index=True)
        else:
            st.info("No clinical data available for drift analysis.")

    # Prediction drift
    st.markdown("### Prediction Distribution Drift")
    pred_drift = AnomalyDetector.detect_prediction_distribution_anomaly()
    if pred_drift.get("status") == "INSUFFICIENT_DATA":
        st.info(pred_drift.get("message", "Insufficient data."))
    else:
        drift_status = pred_drift.get("status", "UNKNOWN")
        if drift_status == "HEALTHY":
            st.success(f"Prediction distribution: {drift_status}")
        elif drift_status == "WARNING":
            st.warning(f"Prediction distribution: {drift_status} — Distribution shift detected.")
        else:
            st.error(f"Prediction distribution: {drift_status}")

        if pred_drift.get("reference_distribution") and pred_drift.get("current_distribution"):
            import pandas as pd
            ref = pred_drift["reference_distribution"]
            cur = pred_drift["current_distribution"]
            all_cats = sorted(set(ref.keys()) | set(cur.keys()))
            df = pd.DataFrame([
                {"Category": cat, "Reference": f"{ref.get(cat, 0):.1%}", "Current": f"{cur.get(cat, 0):.1%}"}
                for cat in all_cats
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as exc:
    st.warning(f"Unable to load drift analysis: {exc}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 📋 Data Quality")

try:
    dq_result = DataQualityMonitor.assess_data_quality()
    dq_status = dq_result.get("status", "UNKNOWN")

    dq1, dq2, dq3, dq4 = st.columns(4)
    with dq1:
        st.metric("Total Records", dq_result.get("total_records", 0))
    with dq2:
        st.metric("Valid Records", dq_result.get("valid_records", 0))
    with dq3:
        st.metric("Duplicate Rate", f"{dq_result.get('duplicate_rate', 0):.2%}")
    with dq4:
        status_fn = {"HEALTHY": st.success, "WARNING": st.warning, "DEGRADED": st.error}.get(dq_status, st.info)
        status_fn(f"Quality: {dq_status}")

    if dq_result.get("issues"):
        for issue in dq_result["issues"]:
            st.warning(issue)

    # Missing data analysis
    missing = dq_result.get("missing_analysis", {})
    if missing.get("per_feature"):
        st.markdown("### Missing Data by Feature")
        import pandas as pd
        rows = [
            {"Feature": feat, "Missing Count": info["count"], "Missing Rate": f"{info['rate']:.2%}"}
            for feat, info in missing["per_feature"].items()
            if info["count"] > 0
        ]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.success("No missing data detected.")

    # Schema analysis
    schema = dq_result.get("schema_analysis", {})
    if schema.get("unexpected_categories"):
        st.markdown("### Schema Issues")
        for feat, cats in schema["unexpected_categories"].items():
            st.warning(f"Unexpected categories in `{feat}`: {cats}")

except Exception as exc:
    st.warning(f"Unable to load data quality: {exc}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## ⚡ System Performance")

try:
    perf = PerformanceMonitor.get_system_performance_summary(hours=24)
    p1, p2, p3 = st.columns(3)
    with p1:
        latency = perf.get("inference_latency", {})
        st.metric("Avg Inference Latency", f"{latency.get('avg_value', 0):.1f} ms")
    with p2:
        errors = perf.get("errors", {})
        st.metric("Error Rate", f"{errors.get('error_rate', 0):.2%}")
    with p3:
        st.metric("Total Requests", perf.get("requests", {}).get("count", 0))

    # Latency trend
    latency_trend = PerformanceMonitor.get_latency_trend(hours=24)
    if latency_trend:
        st.markdown("### Latency Trend (24h)")
        import pandas as pd
        import altair as alt
        df = pd.DataFrame(latency_trend)
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("period:T", title="Time"),
            y=alt.Y("avg_latency_ms:Q", title="Avg Latency (ms)"),
        ).properties(title="Inference Latency Trend", height=200)
        render_chart(chart)

except Exception as exc:
    st.warning(f"Unable to load performance data: {exc}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# MONITORING EVENTS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 📋 Monitoring Events")

try:
    event_counts = MonitoringEventService.get_event_counts()
    ev1, ev2, ev3, ev4 = st.columns(4)
    with ev1:
        st.metric("Total Events", event_counts.get("total", 0))
    with ev2:
        open_count = event_counts.get("by_status", {}).get("OPEN", 0)
        st.metric("Open Events", open_count)
    with ev3:
        warning_count = event_counts.get("by_severity", {}).get("WARNING", 0)
        st.metric("Warnings", warning_count)
    with ev4:
        critical_count = event_counts.get("by_severity", {}).get("CRITICAL", 0)
        st.metric("Critical", critical_count)

    events = MonitoringEventService.get_recent_events(limit=20)
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

# ── Disclaimer ───────────────────────────────────────────────────────────────
st.markdown(
    "> **Disclaimer:** All monitoring thresholds are engineering thresholds, NOT clinical thresholds. "
    "Drift warnings indicate data distribution differences, not medical safety issues. "
    "Model monitoring supports human review; it does not automatically determine clinical validity."
)
