"""Chart preparation and visualization components for HeartGuard (Phase 12).

Provides Altair-based visual representations for:
  - Risk Trends (historical timeline, bounded 0-100% scale, tooltips)
  - Risk Components (Clinical 70% vs Lifestyle 30% vs Multimodal Overall)
  - SHAP Explainability (Feature influence on model prediction)
  - Admin/Reviewer Distributions (Risk categories, Review statuses, Alert outcomes)

SAFETY RULE:
  SHAP factors are strictly described as "model contributions" or "factors
  influencing this model output" — never as "causes", "proof", or "diagnoses".
"""

from __future__ import annotations

from typing import Any
import altair as alt
import pandas as pd
import streamlit as st


# HeartGuard color palette tokens
PALETTE = {
    "primary": "#1e3a8a",       # Deep medical navy
    "clinical": "#0284c7",      # Sky blue (Clinical 70%)
    "lifestyle": "#10b981",     # Emerald green (Lifestyle 30%)
    "overall": "#4f46e5",       # Indigo (Overall Multimodal)
    "low": "#16a34a",           # Green
    "elevated": "#d97706",      # Amber
    "high": "#ea580c",          # Orange
    "critical": "#dc2626",      # Red
    "pending": "#ca8a04",       # Yellow-gold
    "in_review": "#2563eb",     # Blue
    "accepted": "#16a34a",      # Green
    "modified": "#9333ea",      # Purple
    "rejected": "#dc2626",      # Red
    "neutral": "#6b7280",       # Gray
}


def prepare_risk_trend_chart(trends: list[dict[str, Any]]) -> alt.Chart | None:
    """Build an Altair line-and-point chart for chronological risk trajectories.

    Args:
        trends: List of dicts with keys 'date' (YYYY-MM-DD), 'overall_risk',
                'clinical_risk', 'lifestyle_risk', 'risk_category'.
                Must be sorted oldest -> newest.

    Returns:
        alt.Chart or None if insufficient data.
    """
    if not trends or len(trends) < 2:
        return None

    # Ensure chronological sort
    sorted_trends = sorted(trends, key=lambda x: str(x.get("date", "")))

    data = []
    for item in sorted_trends:
        data.append(
            {
                "Date": str(item.get("date", "")),
                "Overall Risk (%)": round(float(item.get("overall_risk", 0.0)), 1),
                "Clinical Risk (%)": round(float(item.get("clinical_risk", 0.0)), 1),
                "Lifestyle Risk (%)": round(float(item.get("lifestyle_risk", 0.0)), 1),
                "Category": str(item.get("risk_category", "Unknown")),
                "Assessment ID": str(item.get("assessment_id", "")),
            }
        )

    df = pd.DataFrame(data)

    base = alt.Chart(df).encode(
        x=alt.X("Date:T", title="Assessment Date", axis=alt.Axis(format="%b %d, %Y")),
        y=alt.Y(
            "Overall Risk (%):Q",
            title="Overall Model-Based Risk (%)",
            scale=alt.Scale(domain=[0, 100]),
        ),
        tooltip=[
            alt.Tooltip("Date:T", title="Date", format="%Y-%m-%d"),
            alt.Tooltip("Overall Risk (%):Q", title="Overall Risk"),
            alt.Tooltip("Clinical Risk (%):Q", title="Clinical (70%)"),
            alt.Tooltip("Lifestyle Risk (%):Q", title="Lifestyle (30%)"),
            alt.Tooltip("Category:N", title="Category"),
            alt.Tooltip("Assessment ID:N", title="ID"),
        ],
    )

    line = base.mark_line(
        color=PALETTE["primary"],
        strokeWidth=3,
        point=True,
    )
    points = base.mark_point(
        size=70,
        color=PALETTE["primary"],
        filled=True,
    )

    chart = (
        (line + points)
        .properties(
            title="Multimodal Risk Score Trajectory Over Time",
            height=320,
        )
        .interactive()
    )
    return chart


def prepare_risk_components_chart(
    clinical_risk: float | None,
    lifestyle_risk: float | None,
    overall_risk: float | None,
) -> alt.Chart | None:
    """Build an Altair bar chart comparing Clinical, Lifestyle, and Overall risk."""
    if clinical_risk is None or lifestyle_risk is None or overall_risk is None:
        return None

    df = pd.DataFrame(
        [
            {
                "Component": "Clinical Risk (70%)",
                "Risk (%)": round(float(clinical_risk), 1),
                "Category": "Clinical",
            },
            {
                "Component": "Lifestyle Risk (30%)",
                "Risk (%)": round(float(lifestyle_risk), 1),
                "Category": "Lifestyle",
            },
            {
                "Component": "Overall Multimodal",
                "Risk (%)": round(float(overall_risk), 1),
                "Category": "Multimodal",
            },
        ]
    )

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Component:N", title=None, sort=None),
            y=alt.Y(
                "Risk (%):Q",
                title="Calculated Risk (%)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            color=alt.Color(
                "Category:N",
                scale=alt.Scale(
                    domain=["Clinical", "Lifestyle", "Multimodal"],
                    range=[PALETTE["clinical"], PALETTE["lifestyle"], PALETTE["overall"]],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Component:N", title="Component"),
                alt.Tooltip("Risk (%):Q", title="Risk Score"),
            ],
        )
        .properties(
            title="Multimodal Component Comparison",
            height=260,
        )
    )
    return chart


def prepare_shap_chart(
    shap_factors: list[dict[str, Any]],
    top_n: int = 8,
) -> alt.Chart | None:
    """Build a horizontal bar chart displaying SHAP feature contributions.

    Args:
        shap_factors: List of dicts with 'feature' (str) and 'shap_value' or 'importance' (float).
        top_n: Max factors to display.

    Returns:
        alt.Chart or None.
    """
    if not shap_factors:
        return None

    data = []
    for item in shap_factors[:top_n]:
        feature = str(item.get("feature", item.get("name", "Unknown")))
        val = item.get("shap_value", item.get("importance", item.get("value", 0.0)))
        try:
            val_float = round(float(val), 4)
        except (ValueError, TypeError):
            val_float = 0.0
        data.append(
            {
                "Feature": feature.replace("_", " ").title(),
                "Influence": val_float,
                "Direction": "Increases Model Risk" if val_float >= 0 else "Decreases Model Risk",
            }
        )

    if not data:
        return None

    df = pd.DataFrame(data)

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadius=3)
        .encode(
            y=alt.Y("Feature:N", sort="-x", title="Clinical Feature"),
            x=alt.X("Influence:Q", title="SHAP Value (Feature Influence on Model Prediction)"),
            color=alt.Color(
                "Direction:N",
                scale=alt.Scale(
                    domain=["Increases Model Risk", "Decreases Model Risk"],
                    range=[PALETTE["critical"], PALETTE["clinical"]],
                ),
                legend=alt.Legend(title="Influence Direction", orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("Feature:N", title="Feature"),
                alt.Tooltip("Influence:Q", title="SHAP Influence", format=".4f"),
                alt.Tooltip("Direction:N", title="Direction"),
            ],
        )
        .properties(
            title="Top Factors Influencing Model Output (SHAP)",
            height=max(180, len(data) * 28),
        )
    )
    return chart


def prepare_category_distribution_chart(cat_dist: dict[str, int]) -> alt.Chart | None:
    """Build a bar chart for risk category distribution."""
    if not cat_dist:
        return None

    data = [{"Category": k, "Count": v} for k, v in cat_dist.items()]
    df = pd.DataFrame(data)

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Category:N", title="Risk Category", sort="-y"),
            y=alt.Y("Count:Q", title="Total Assessments"),
            color=alt.Color(
                "Category:N",
                scale=alt.Scale(
                    domain=["Low", "Elevated", "High", "Critical", "LOW", "ELEVATED", "HIGH", "CRITICAL"],
                    range=[
                        PALETTE["low"], PALETTE["elevated"], PALETTE["high"], PALETTE["critical"],
                        PALETTE["low"], PALETTE["elevated"], PALETTE["high"], PALETTE["critical"],
                    ],
                ),
                legend=None,
            ),
            tooltip=[alt.Tooltip("Category:N"), alt.Tooltip("Count:Q")],
        )
        .properties(title="Risk Category Distribution", height=240)
    )
    return chart


def prepare_review_distribution_chart(review_dist: dict[str, int]) -> alt.Chart | None:
    """Build a bar chart for review status distribution."""
    if not review_dist:
        return None

    data = [{"Status": k.replace("_", " ").title(), "Count": v} for k, v in review_dist.items()]
    df = pd.DataFrame(data)

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Status:N", title="Review Status", sort="-y"),
            y=alt.Y("Count:Q", title="Total Reviews"),
            color=alt.Color(
                "Status:N",
                scale=alt.Scale(
                    domain=["Pending", "In Review", "Accepted", "Modified", "Rejected"],
                    range=[
                        PALETTE["pending"], PALETTE["in_review"], PALETTE["accepted"],
                        PALETTE["modified"], PALETTE["rejected"],
                    ],
                ),
                legend=None,
            ),
            tooltip=[alt.Tooltip("Status:N"), alt.Tooltip("Count:Q")],
        )
        .properties(title="Review Status Distribution", height=240)
    )
    return chart


def prepare_alert_distribution_chart(alert_dist: dict[str, int]) -> alt.Chart | None:
    """Build a bar chart for alert outcomes."""
    if not alert_dist:
        return None

    data = [{"Outcome": k.replace("_", " ").title(), "Count": v} for k, v in alert_dist.items()]
    df = pd.DataFrame(data)

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Outcome:N", title="Alert Outcome", sort="-y"),
            y=alt.Y("Count:Q", title="Total Events"),
            color=alt.value(PALETTE["clinical"]),
            tooltip=[alt.Tooltip("Outcome:N"), alt.Tooltip("Count:Q")],
        )
        .properties(title="Alert Dispatch Statistics", height=240)
    )
    return chart


def render_chart(chart: alt.Chart | None, use_container_width: bool = True) -> None:
    """Helper to render an Altair chart in Streamlit safely."""
    if chart is not None:
        st.altair_chart(chart, use_container_width=use_container_width)
