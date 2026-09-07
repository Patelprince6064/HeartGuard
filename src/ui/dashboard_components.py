"""High-level layout components, headers, empty states, and error wrappers for HeartGuard (Phase 12).

Provides:
  - Header with personalized welcome greeting and academic prototype disclaimer
  - Empty dashboard state for new users
  - Quick action buttons (role-aware)
  - Structured lifestyle insights visualization
  - Safe component wrapper to prevent cascade crashes
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional
import streamlit as st

from src.ui.cards import render_medical_disclaimer

logger = logging.getLogger(__name__)


def render_dashboard_header(
    user_name: str | None,
    user_role: str = "PATIENT",
    subtitle: str = "AI-Powered Heart Disease Risk Assessment",
) -> None:
    """Render the standard HeartGuard dashboard header with personalized greeting."""
    st.title("❤️ HEARTGUARD")
    st.subheader(subtitle)

    greeting = f"Welcome back, {user_name}." if user_name else "Welcome back."
    st.markdown(f"### {greeting}")
    st.caption(f"Role: `{user_role}` · Academic / Research Prototype")

    render_medical_disclaimer()
    st.divider()


def render_empty_dashboard_state() -> None:
    """Render a helpful empty state when a patient has zero completed assessments."""
    with st.container(border=True):
        st.markdown("### 📋 No assessments yet.")
        st.markdown(
            "You have not completed any HeartGuard risk evaluations. "
            "Complete your first multimodal assessment to generate your baseline risk score, "
            "SHAP explainability breakdown, and track your trajectory over time."
        )
        st.page_link(
            "pages/risk_assessment.py",
            label="🩺 Start Your First HeartGuard Assessment →",
        )


def render_quick_actions(
    has_assessments: bool = False,
    is_reviewer_role: bool = False,
    is_admin_role: bool = False,
) -> None:
    """Render role-aware quick action buttons."""
    st.markdown("### ⚡ Quick Actions")
    cols = st.columns(4 if has_assessments else 3)

    with cols[0]:
        st.page_link("pages/risk_assessment.py", label="🩺 New Assessment", use_container_width=True)

    with cols[1]:
        st.page_link("pages/lifestyle_analyzer.py", label="🏃 Lifestyle Analysis", use_container_width=True)

    with cols[2]:
        st.page_link("pages/history.py", label="📜 History & Analytics", use_container_width=True)

    if has_assessments and len(cols) > 3:
        with cols[3]:
            st.page_link("pages/history.py", label="📑 Generate Latest Report", use_container_width=True)

    if is_reviewer_role:
        st.page_link("pages/review.py", label="🩺 Open Doctor Review Portal →")
    if is_admin_role:
        st.page_link("pages/admin.py", label="🛡️ Open Admin Dashboard →")


def render_lifestyle_insights(lifestyle_factors: list[dict[str, Any]] | None) -> None:
    """Render structured lifestyle factor contributions if present in assessment data.

    Supported categories from HeartGuard Lifestyle NLP:
      - smoking, physical_activity, diet, stress, sleep, alcohol, sedentary_behavior
    """
    if not lifestyle_factors:
        st.info("Structured lifestyle factor breakdowns are not available for this assessment.")
        return

    st.markdown("#### 🏃 Lifestyle Risk Drivers")
    cols = st.columns(min(4, len(lifestyle_factors)))
    for idx, factor in enumerate(lifestyle_factors):
        col = cols[idx % len(cols)]
        name = str(factor.get("category", factor.get("factor", factor.get("name", "Habit")))).replace("_", " ").title()
        risk_level = str(factor.get("level", factor.get("risk", factor.get("score", "Moderate"))))
        notes = factor.get("matched_terms", factor.get("notes", ""))
        with col:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(f"Risk factor: `{risk_level}`")
                if notes:
                    if isinstance(notes, list):
                        st.caption("Matches: " + ", ".join(str(n) for n in notes[:3]))
                    else:
                        st.caption(f"Details: {notes}")


def safe_render_section(section_name: str, render_fn: Callable[[], None]) -> None:
    """Execute a dashboard section within a safe boundary.

    If an unexpected error occurs, display a friendly notice and log the error
    without crashing the rest of the dashboard page.
    """
    try:
        render_fn()
    except Exception as exc:
        logger.exception("Error rendering dashboard section '%s': %s", section_name, exc)
        st.warning(f"Unable to load {section_name}. Please try refreshing the page.")
