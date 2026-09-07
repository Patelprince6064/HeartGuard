"""Standardized card components and disclaimers for HeartGuard (Phase 12).

Provides reusable UI card containers for:
  - Metric KPIs (Latest Risk, Total Assessments, Category, Review Status, Alert Status)
  - Risk Component Breakdown (Clinical 70% + Lifestyle 30% -> Multimodal Overall)
  - Assessment Summary Card
  - Medical Disclaimers and Emergency Clinical Safety Banners
"""

from __future__ import annotations

from typing import Any, Optional
import streamlit as st

from src.ui.badges import (
    get_alert_status_badge,
    get_priority_badge,
    get_risk_category_badge,
    get_review_status_badge,
)


def format_risk_percentage(value: float | int | None) -> str:
    """Format a numerical risk score into a consistent percentage string (e.g. 72.4%)."""
    if value is None:
        return "N/A"
    try:
        # Handle cases where value might be given as 0.0 - 1.0 or 0.0 - 100.0
        # In HeartGuard, overall_risk is stored on a 0 - 100 scale
        num = float(value)
        return f"{num:.1f}%"
    except (ValueError, TypeError):
        return "N/A"


def render_medical_disclaimer() -> None:
    """Render the standard, unobtrusive medical research disclaimer."""
    st.info(
        "ℹ️ **Academic & Research Prototype Notice**\n\n"
        "HeartGuard is an academic/research prototype. Its AI-generated risk assessment "
        "is an experimental statistical estimate, **not a medical diagnosis**, and should "
        "never replace comprehensive clinical evaluation by a qualified healthcare professional."
    )


def render_emergency_disclaimer() -> None:
    """Render the prominent clinical emergency disclaimer for high/critical states."""
    st.error(
        "🚨 **Emergency Medical Notice**\n\n"
        "If you or someone nearby is experiencing severe symptoms — such as persistent "
        "chest pain, pressure or tightness, shortness of breath, sudden numbness, or dizziness — "
        "**seek immediate emergency medical attention or call your local emergency services (e.g., 911 / 112 / 108)**."
    )


def render_trend_disclaimer() -> None:
    """Render the required disclaimer for historical risk trajectory graphs."""
    st.caption(
        "Changes in HeartGuard model-based risk scores reflect changes in assessment inputs "
        "and model outputs. They do not by themselves establish disease progression."
    )


def render_metric_card(
    title: str,
    value: str,
    caption: Optional[str] = None,
    badge_md: Optional[str] = None,
    help_text: Optional[str] = None,
) -> None:
    """Render a clean metric container with accessible typography and badges."""
    with st.container(border=True):
        st.markdown(f"##### {title}")
        st.markdown(f"## {value}")
        if badge_md:
            st.markdown(badge_md)
        if caption:
            st.caption(caption)
        if help_text:
            st.caption(f"ℹ️ {help_text}")


def render_risk_components_cards(
    clinical_risk: float | None,
    lifestyle_risk: float | None,
    overall_risk: float | None,
) -> None:
    """Render side-by-side cards breaking down multimodal components."""
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("##### Clinical ML Risk")
            st.markdown(f"### {format_risk_percentage(clinical_risk)}")
            st.caption("Weight: **70%** · Derived from clinical lab & vitals")

    with col2:
        with st.container(border=True):
            st.markdown("##### Lifestyle NLP Risk")
            st.markdown(f"### {format_risk_percentage(lifestyle_risk)}")
            st.caption("Weight: **30%** · Derived from lifestyle habits text")

    with col3:
        with st.container(border=True):
            st.markdown("##### Multimodal Overall Risk")
            st.markdown(f"### {format_risk_percentage(overall_risk)}")
            st.caption("Combined Model Score (70% Clinical + 30% Lifestyle)")


def render_assessment_summary_card(
    assessment_id: str,
    created_at: str,
    overall_risk: float,
    clinical_risk: float,
    lifestyle_risk: float,
    risk_category: str,
    recommendation: str,
    alert_status: str,
    review_status: str | None = None,
    show_view_button: bool = True,
    button_key_prefix: str = "summary",
) -> None:
    """Render a structured summary card for a specific assessment."""
    with st.container(border=True):
        st.markdown(f"#### Assessment `{assessment_id}`")
        st.caption(f"📅 Completed on: **{created_at[:10]}** ({created_at[11:16]} UTC)")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Model Risk", format_risk_percentage(overall_risk))
            st.markdown(get_risk_category_badge(risk_category))
        with col_b:
            st.metric("Review Status", review_status or "PENDING")
            st.markdown(get_review_status_badge(review_status))
        with col_c:
            st.metric("Alert Status", alert_status or "NOT_TRIGGERED")
            st.markdown(get_alert_status_badge(alert_status))

        st.markdown("**Clinical Guidance Recommendation:**")
        st.info(recommendation)

        if show_view_button:
            st.page_link(
                "pages/history.py",
                label="🔍 View Assessment in History & Download Report →",
            )


def render_recommendation_card(rec: Any) -> None:
    """Render an accessible card for a personalized non-diagnostic recommendation."""
    if hasattr(rec, "to_dict"):
        data = rec.to_dict()
    elif isinstance(rec, dict):
        data = rec
    else:
        return

    title = data.get("title", "Recommendation")
    desc = data.get("description", "")
    priority = data.get("priority", "INFO")
    category = data.get("category", "General")
    source = data.get("source", "Rule Engine")

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{title}**")
            st.caption(f"📁 Category: **{category}** · Source: `{source}`")
        with col2:
            st.markdown(get_priority_badge(priority))

        st.markdown(desc)


def render_insight_card(
    title: str,
    description: str,
    source: str = "AI Multimodal Engine",
    caption: str | None = None,
) -> None:
    """Render an individual AI insight highlight card."""
    with st.container(border=True):
        st.markdown(f"##### {title}")
        st.markdown(description)
        sub = f"Source: `{source}`"
        if caption:
            sub += f" · {caption}"
        st.caption(sub)

