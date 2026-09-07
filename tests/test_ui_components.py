"""Tests for HeartGuard UI components, badges, cards, and chart preparation (Phase 12).

Covers:
  - Accessible badges for risk categories, review statuses, and alert outcomes
  - Percentage formatting
  - Altair chart preparation helpers and boundary conditions
  - Empty states and degradation fallbacks
"""

from __future__ import annotations

import altair as alt
import pytest

from src.ui.badges import (
    get_alert_status_badge,
    get_review_status_badge,
    get_risk_category_badge,
)
from src.ui.cards import format_risk_percentage
from src.ui.charts import (
    prepare_alert_distribution_chart,
    prepare_category_distribution_chart,
    prepare_review_distribution_chart,
    prepare_risk_components_chart,
    prepare_risk_trend_chart,
    prepare_shap_chart,
)


# ── Badge Formatters ─────────────────────────────────────────────────────────

def test_risk_category_badges():
    assert "LOW RISK" in get_risk_category_badge("LOW")
    assert "ELEVATED RISK" in get_risk_category_badge("ELEVATED")
    assert "HIGH RISK" in get_risk_category_badge("HIGH")
    assert "CRITICAL RISK" in get_risk_category_badge("CRITICAL")
    # Case insensitivity
    assert "LOW RISK" in get_risk_category_badge("lower_risk")
    # Unknown / None
    assert "UNKNOWN" in get_risk_category_badge(None)
    assert "OTHER" in get_risk_category_badge("OTHER")


def test_review_status_badges():
    assert "PENDING REVIEW" in get_review_status_badge("PENDING")
    assert "IN REVIEW" in get_review_status_badge("IN_REVIEW")
    assert "ACCEPTED" in get_review_status_badge("ACCEPTED")
    assert "MODIFIED" in get_review_status_badge("MODIFIED")
    assert "DISCORDANT" in get_review_status_badge("REJECTED")
    assert "NOT REVIEWED" in get_review_status_badge(None)


def test_alert_status_badges():
    assert "NOT TRIGGERED" in get_alert_status_badge("NOT_TRIGGERED")
    assert "TRIGGERED" in get_alert_status_badge("TRIGGERED")
    assert "ALERT SENT" in get_alert_status_badge("SENT")
    assert "ALERT FAILED" in get_alert_status_badge("FAILED")
    assert "NOT TRIGGERED" in get_alert_status_badge(None)


# ── Card & String Formatters ─────────────────────────────────────────────────

def test_format_risk_percentage():
    assert format_risk_percentage(72.4) == "72.4%"
    assert format_risk_percentage(100) == "100.0%"
    assert format_risk_percentage(0.0) == "0.0%"
    assert format_risk_percentage("45.67") == "45.7%"
    assert format_risk_percentage(None) == "N/A"
    assert format_risk_percentage("invalid") == "N/A"


# ── Chart Preparation ────────────────────────────────────────────────────────

def test_prepare_risk_trend_chart_empty():
    # 0 or 1 item returns None
    assert prepare_risk_trend_chart([]) is None
    assert prepare_risk_trend_chart([{"date": "2026-01-01", "overall_risk": 50.0}]) is None


def test_prepare_risk_trend_chart_valid():
    trends = [
        {"date": "2026-01-01", "overall_risk": 40.0, "clinical_risk": 45.0, "lifestyle_risk": 30.0, "risk_category": "LOW"},
        {"date": "2026-02-01", "overall_risk": 60.0, "clinical_risk": 65.0, "lifestyle_risk": 45.0, "risk_category": "ELEVATED"},
    ]
    chart = prepare_risk_trend_chart(trends)
    assert chart is not None
    assert isinstance(chart, alt.Chart) or isinstance(chart, alt.LayerChart)


def test_prepare_risk_components_chart():
    assert prepare_risk_components_chart(None, 50.0, 50.0) is None
    chart = prepare_risk_components_chart(60.0, 40.0, 54.0)
    assert chart is not None
    assert isinstance(chart, alt.Chart)


def test_prepare_shap_chart():
    assert prepare_shap_chart([]) is None
    assert prepare_shap_chart(None) is None

    factors = [
        {"feature": "RestingBP", "shap_value": 0.15},
        {"feature": "Cholesterol", "shap_value": -0.08},
    ]
    chart = prepare_shap_chart(factors, top_n=5)
    assert chart is not None
    assert isinstance(chart, alt.Chart)


def test_prepare_distribution_charts():
    cat_chart = prepare_category_distribution_chart({"LOW": 5, "ELEVATED": 3})
    assert cat_chart is not None
    assert prepare_category_distribution_chart({}) is None

    rev_chart = prepare_review_distribution_chart({"PENDING": 2, "ACCEPTED": 4})
    assert rev_chart is not None
    assert prepare_review_distribution_chart({}) is None

    alert_chart = prepare_alert_distribution_chart({"NOT_TRIGGERED": 6, "SENT": 1})
    assert alert_chart is not None
    assert prepare_alert_distribution_chart({}) is None
