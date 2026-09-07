"""Patient Dashboard for HeartGuard (Phase 12).

Upgrades the HeartGuard dashboard into a professional, responsive AI healthcare
research application interface.

STRUCTURE:
  - Welcome banner with personalized authenticated greeting and research disclaimer
  - Top metric KPI cards: Latest Risk, Category, Assessment Count, Review Status, Alert Status
  - Latest assessment summary panel
  - Risk component breakdown cards & chart (Clinical 70% vs Lifestyle 30% vs Overall)
  - Chronological risk trend chart with delta interpretation and required disclaimers
  - Top model factors (SHAP) feature contribution chart (strictly non-diagnostic wording)
  - Structured lifestyle insights
  - Recent assessments table with "View All" link
  - Role-aware quick actions
  - System health / pipeline status (in collapsible section)

SAFETY INVARIANTS:
  - Does NOT retrain or run ML models on page load (reads stored results only).
  - Never uses diagnostic language ("proof", "diagnosis", "cause").
  - Includes prominent research prototype and emergency medical notices.
"""

from __future__ import annotations

import json
from pathlib import Path
import streamlit as st

from config.settings import (
    MODEL_DIRECTORY,
    PROCESSED_DATA_DIRECTORY,
    PROJECT_NAME,
    RAW_DATA_DIRECTORY,
    REPORT_DIRECTORY,
)
from src.analytics.analytics_service import AnalyticsService
from src.analytics.history_service import HistoryService
from src.analytics.trend_service import TrendService
from src.auth.authorization import is_admin, is_reviewer, require_authentication
from src.auth.session_manager import clear_session, get_current_user
from src.security.audit_logger import log_event
from src.ui import (
    format_risk_percentage,
    get_alert_status_badge,
    get_review_status_badge,
    get_risk_category_badge,
    prepare_risk_components_chart,
    prepare_risk_trend_chart,
    prepare_shap_chart,
    render_assessment_summary_card,
    render_chart,
    render_dashboard_header,
    render_emergency_disclaimer,
    render_empty_dashboard_state,
    render_insight_card,
    render_lifestyle_insights,
    render_medical_disclaimer,
    render_metric_card,
    render_quick_actions,
    render_recent_assessments_table,
    render_recommendation_card,
    render_risk_components_cards,
    render_trend_disclaimer,
    safe_render_section,
)

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{PROJECT_NAME} — Patient Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Authorization Guard ───────────────────────────────────────────────────────
require_authentication()
current_user = get_current_user()
user_id: int = current_user["id"]
user_name: str = current_user.get("name", "")
user_role: str = current_user.get("role", "PATIENT")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**{user_name or 'User'}**")
    st.caption(f"Role: `{user_role}`")
    st.divider()
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/risk_assessment.py", label="🩺 New Assessment")
    st.page_link("pages/lifestyle_analyzer.py", label="🏃 Lifestyle Analyzer")
    st.page_link("pages/history.py", label="📜 History & Reports")
    st.page_link("pages/explainable_ai.py", label="🧬 Explainable AI")
    if is_reviewer():
        st.page_link("pages/review.py", label="🩺 Doctor Review")
    if is_admin():
        st.page_link("pages/admin.py", label="🛡️ Admin Dashboard")
    st.page_link("pages/security.py", label="🔐 Security & Profile")
    st.divider()
    if st.button("🚪 Log Out", use_container_width=True, key="dashboard_logout"):
        log_event("logout", "SUCCESS", user_id=user_id, role=user_role)
        clear_session()
        st.switch_page("pages/login.py")

# ── Header & Academic Disclaimer ──────────────────────────────────────────────
render_dashboard_header(user_name=user_name, user_role=user_role)

# ── Load User Stored Data ─────────────────────────────────────────────────────
stats = AnalyticsService.calculate_user_statistics(user_id=user_id)
total_assessments = stats.get("total_assessments", 0)

# ── Empty State Handling ──────────────────────────────────────────────────────
if total_assessments == 0:
    render_empty_dashboard_state()
    st.divider()
    render_quick_actions(has_assessments=False, is_reviewer_role=is_reviewer(), is_admin_role=is_admin())
    st.stop()

# ── Top Metric Cards (KPI Row) ────────────────────────────────────────────────
def _render_kpis() -> None:
    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        latest_risk = stats.get("latest_risk")
        render_metric_card(
            title="Model-Based Risk",
            value=format_risk_percentage(latest_risk),
            caption="Experimental AI estimate",
            help_text="Multimodal probability score (0-100%). Not a medical diagnosis.",
        )

    with k2:
        category = stats.get("latest_category") or "Unknown"
        cat_badge = get_risk_category_badge(category)
        render_metric_card(
            title="Risk Category",
            value=category.upper(),
            badge_md=cat_badge,
            caption="Baseline risk tier",
        )

    with k3:
        render_metric_card(
            title="Total Assessments",
            value=str(total_assessments),
            caption="Completed evaluations",
        )

    with k4:
        rev_status = stats.get("latest_review_status") or "NOT_REVIEWED"
        rev_badge = get_review_status_badge(rev_status)
        render_metric_card(
            title="Professional Review",
            value=rev_status.replace("_", " ").title(),
            badge_md=rev_badge,
            caption="Clinical reviewer status",
        )

    with k5:
        alert_status = stats.get("latest_alert_status") or "NOT_TRIGGERED"
        alert_badge = get_alert_status_badge(alert_status)
        render_metric_card(
            title="Latest Alert Status",
            value=alert_status.replace("_", " ").title(),
            badge_md=alert_badge,
            caption="Emergency notification state",
        )

safe_render_section("Summary Metrics", _render_kpis)
st.divider()

# ── Emergency Notice if High / Critical ───────────────────────────────────────
latest_cat_upper = str(stats.get("latest_category", "")).upper()
if "CRITICAL" in latest_cat_upper or "HIGH" in latest_cat_upper:
    render_emergency_disclaimer()
    st.divider()

# ── Latest Assessment Summary ─────────────────────────────────────────────────
latest_assessment = HistoryService.get_latest_assessment(user_id=user_id)
previous_assessment = HistoryService.get_previous_assessment(user_id=user_id)
comparison = TrendService.compare_assessments(latest_assessment, previous_assessment)

if latest_assessment:
    st.markdown("### 📌 Latest Assessment")
    col_sum_a, col_sum_b = st.columns([3, 2])

    with col_sum_a:
        render_assessment_summary_card(
            assessment_id=latest_assessment.assessment_id,
            created_at=latest_assessment.created_at,
            overall_risk=latest_assessment.overall_risk,
            clinical_risk=latest_assessment.clinical_risk,
            lifestyle_risk=latest_assessment.lifestyle_risk,
            risk_category=latest_assessment.risk_category,
            recommendation=latest_assessment.recommendation,
            alert_status=latest_assessment.alert_status,
            review_status=stats.get("latest_review_status"),
            show_view_button=True,
        )

    with col_sum_b:
        with st.container(border=True):
            st.markdown("#### Assessment Comparison")
            if comparison:
                st.markdown(f"**Trajectory:** `{comparison['trend_direction']}`")
                st.markdown(comparison["interpretation"])
                delta_str = comparison["overall_risk"]["delta_str"]
                st.metric(
                    "Change from Previous Assessment",
                    f"{comparison['overall_risk']['latest']:.1f}%",
                    delta_str,
                )
                if comparison["category"]["changed"]:
                    st.warning(
                        f"Category shifted from {comparison['category']['previous']} "
                        f"to {comparison['category']['latest']}."
                    )
            else:
                st.info(
                    "This is your baseline assessment. Complete future evaluations "
                    "to compare delta trajectories over time."
                )

    st.divider()

# ── Risk Components Breakdown ─────────────────────────────────────────────────
def _render_components_section() -> None:
    if not latest_assessment:
        return
    st.markdown("### 🔬 Risk Component Decomposition")
    st.caption("HeartGuard decomposes multimodal risk into clinical and lifestyle dimensions.")
    render_risk_components_cards(
        clinical_risk=latest_assessment.clinical_risk,
        lifestyle_risk=latest_assessment.lifestyle_risk,
        overall_risk=latest_assessment.overall_risk,
    )

    chart = prepare_risk_components_chart(
        clinical_risk=latest_assessment.clinical_risk,
        lifestyle_risk=latest_assessment.lifestyle_risk,
        overall_risk=latest_assessment.overall_risk,
    )
    if chart is not None:
        render_chart(chart)

safe_render_section("Risk Components", _render_components_section)
st.divider()

# ── Risk Trajectory Trend ─────────────────────────────────────────────────────
def _render_trend_section() -> None:
    st.markdown("### 📈 Overall Risk Trend")
    trends = TrendService.get_risk_trends(user_id=user_id)

    if len(trends) < 2:
        st.info(
            "ℹ️ Single-point baseline recorded. Complete at least two assessments "
            "to generate an interactive chronological risk trend line."
        )
    else:
        chart = prepare_risk_trend_chart(trends)
        if chart is not None:
            render_chart(chart)
        else:
            st.warning("Unable to render trend visualization.")

    render_trend_disclaimer()

safe_render_section("Risk Trend", _render_trend_section)
st.divider()

# ── Top Contributing Factors (SHAP) ───────────────────────────────────────────
def _render_shap_section() -> None:
    st.markdown("### 🧬 Top Model Factors (Explainable AI)")
    st.caption(
        "Features with the highest influence on this model output according to SHAP "
        "(SHapley Additive exPlanations). These represent statistical feature contributions, "
        "not medical causality or clinical diagnoses."
    )

    if latest_assessment:
        factors = latest_assessment.get_top_clinical_factors()
        if factors:
            chart = prepare_shap_chart(factors, top_n=8)
            if chart is not None:
                render_chart(chart)
            else:
                st.info("Explainability information is not available for this assessment.")
        else:
            st.info("Explainability information is not available for this assessment.")
    else:
        st.info("No assessment selected for SHAP inspection.")

safe_render_section("Explainability (SHAP)", _render_shap_section)
st.divider()

# ── Structured Lifestyle Insights ─────────────────────────────────────────────
def _render_lifestyle_section() -> None:
    if latest_assessment:
        lifestyle_factors = latest_assessment.get_lifestyle_factors()
        if lifestyle_factors:
            st.markdown("### 🏃 Lifestyle Health Analysis")
            st.caption("Quantified habits extracted via rule-based clinical NLP lexicon.")
            render_lifestyle_insights(lifestyle_factors)
            st.divider()

safe_render_section("Lifestyle Insights", _render_lifestyle_section)

# ── Personalized AI Recommendations & Insights (Phase 13) ─────────────────────
def _render_recommendations_section() -> None:
    if not latest_assessment:
        return
    st.markdown("### 💡 Personalized AI Recommendations & Insights")
    st.caption(
        "Action-oriented guidance derived from your latest multimodal assessment parameters. "
        "These recommendations are educational and strictly non-diagnostic."
    )

    try:
        from src.recommendations.recommendation_service import RecommendationService
        insights = RecommendationService.get_or_create_insights(
            assessment_id=latest_assessment.assessment_id, user_id=user_id
        )

        render_insight_card(
            title="Assessment Summary & Clinical Context",
            description=insights.summary_text,
            source="HeartGuard Recommendation Engine",
        )

        if insights.recommendations:
            st.markdown("#### Priority-Ranked Guidance")
            for rec in insights.recommendations[:5]:
                render_recommendation_card(rec)

            if len(insights.recommendations) > 5:
                with st.expander(f"📋 View All {len(insights.recommendations)} Recommendations", expanded=False):
                    for rec in insights.recommendations[5:]:
                        render_recommendation_card(rec)
        else:
            st.info("No personalized recommendations are available for this assessment.")

    except Exception as exc:
        st.warning("Unable to generate recommendations right now. Your original HeartGuard assessment is still available.")

safe_render_section("AI Recommendations & Insights", _render_recommendations_section)
st.divider()

# ── Recent Assessments Table ──────────────────────────────────────────────────
def _render_recent_table() -> None:
    st.markdown("### 📋 Recent Assessments")
    recent = AnalyticsService.get_user_recent_assessments(user_id=user_id, limit=5)
    render_recent_assessments_table(recent, limit=5, show_full_link=True)

safe_render_section("Recent Assessments", _render_recent_table)
st.divider()

# ── Quick Actions ─────────────────────────────────────────────────────────────
render_quick_actions(
    has_assessments=(total_assessments > 0),
    is_reviewer_role=is_reviewer(),
    is_admin_role=is_admin(),
)
st.divider()

# ── System Health & Pipeline Status (Collapsible) ─────────────────────────────
with st.expander("🛠️ System Health & Machine Learning Pipeline Status"):
    col1, col2, col3, col4 = st.columns(4)

    cleveland_path = RAW_DATA_DIRECTORY / "heart.csv"
    preprocessor_path = MODEL_DIRECTORY / "preprocessor.pkl"
    train_path = PROCESSED_DATA_DIRECTORY / "cleveland_train.csv"
    best_model_path = REPORT_DIRECTORY / "best_model.json"

    with col1:
        st.markdown("**Cleveland Dataset**")
        if cleveland_path.exists():
            st.success("Ready")
        else:
            st.warning("Not Found")

    with col2:
        st.markdown("**Data Preprocessor**")
        if preprocessor_path.exists() and train_path.exists():
            st.success("Ready")
        else:
            st.warning("Not Ready")

    with col3:
        st.markdown("**Clinical ML Model**")
        if best_model_path.exists():
            try:
                best_info = json.loads(best_model_path.read_text())
                st.success(best_info.get("model_name", "Ready").replace("_", " ").title())
            except Exception:
                st.success("Ready")
        else:
            st.warning("Not Trained")

    with col4:
        st.markdown("**Multimodal Engine**")
        if best_model_path.exists():
            st.success("Operational (70/30)")
        else:
            st.warning("ML Required")
