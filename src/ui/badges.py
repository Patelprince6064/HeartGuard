"""Status badge formatters and UI helpers for HeartGuard (Phase 12).

Provides accessible text-and-icon badges for:
  - Risk Categories (LOW, ELEVATED, HIGH, CRITICAL)
  - Review Statuses (PENDING, IN_REVIEW, ACCEPTED, MODIFIED, REJECTED, NOT_REVIEWED)
  - Alert Statuses (NOT_TRIGGERED, TRIGGERED, SENT, FAILED)

ACCESSIBILITY RULE:
  Never rely on color alone to convey status. Every badge must include
  explicit text labels and unambiguous symbolic markers.
"""

from __future__ import annotations

from typing import Any
import streamlit as st


# ── Risk Category Badges ─────────────────────────────────────────────────────

RISK_CATEGORY_CONFIG: dict[str, dict[str, str]] = {
    "LOW": {
        "label": "LOW RISK",
        "icon": "🟢",
        "color": "#16a34a",
        "bg_color": "#dcfce7",
        "description": "Model risk score is within the lower baseline range.",
    },
    "ELEVATED": {
        "label": "ELEVATED RISK",
        "icon": "🟡",
        "color": "#d97706",
        "bg_color": "#fef3c7",
        "description": "Model risk score is moderately elevated.",
    },
    "HIGH": {
        "label": "HIGH RISK",
        "icon": "🟠",
        "color": "#ea580c",
        "bg_color": "#ffedd5",
        "description": "Model risk score indicates high probability factors.",
    },
    "CRITICAL": {
        "label": "CRITICAL RISK",
        "icon": "🔴",
        "color": "#dc2626",
        "bg_color": "#fee2e2",
        "description": "Model risk score is critical; prompt clinical evaluation advised.",
    },
}


def get_risk_category_badge(category: str | None) -> str:
    """Return a formatted markdown badge string for a risk category."""
    if not category:
        return "`⚪ [UNKNOWN CATEGORY]`"
    normalized = category.strip().upper()
    for key, cfg in RISK_CATEGORY_CONFIG.items():
        if key in normalized:
            return f"`{cfg['icon']} [{cfg['label']}]`"
    return f"`⚪ [{category.upper()}]`"


# ── Review Status Badges ─────────────────────────────────────────────────────

REVIEW_STATUS_CONFIG: dict[str, dict[str, str]] = {
    "PENDING": {
        "label": "PENDING REVIEW",
        "icon": "⏳",
        "color": "#ca8a04",
        "bg_color": "#fef9c3",
        "description": "Assessment is awaiting professional human review.",
    },
    "IN_REVIEW": {
        "label": "IN REVIEW",
        "icon": "🔍",
        "color": "#2563eb",
        "bg_color": "#dbeafe",
        "description": "Assessment is currently being examined by a reviewer.",
    },
    "REVIEWED": {
        "label": "REVIEWED",
        "icon": "✅",
        "color": "#16a34a",
        "bg_color": "#dcfce7",
        "description": "Professional review completed.",
    },
    "FOLLOW_UP_RECOMMENDED": {
        "label": "FOLLOW-UP RECOMMENDED",
        "icon": "🔄",
        "color": "#9333ea",
        "bg_color": "#f3e8ff",
        "description": "Reviewer flagged that follow-up is recommended.",
    },
    "CLOSED": {
        "label": "CLOSED",
        "icon": "🔒",
        "color": "#6b7280",
        "bg_color": "#f3f4f6",
        "description": "Review workflow closed.",
    },
    "ACCEPTED": {
        "label": "REVIEWED (ACCEPTED)",
        "icon": "✅",
        "color": "#16a34a",
        "bg_color": "#dcfce7",
        "description": "Review completed with no adjustments noted.",
    },
    "MODIFIED": {
        "label": "REVIEWED (MODIFIED)",
        "icon": "📝",
        "color": "#9333ea",
        "bg_color": "#f3e8ff",
        "description": "Review completed with professional clinical observations.",
    },
    "REJECTED": {
        "label": "REVIEWED (DISCORDANT)",
        "icon": "❌",
        "color": "#dc2626",
        "bg_color": "#fee2e2",
        "description": "Professional reviewer flagged discordant assessment factors.",
    },
    "NOT_REVIEWED": {
        "label": "NOT REVIEWED",
        "icon": "⚪",
        "color": "#6b7280",
        "bg_color": "#f3f4f6",
        "description": "No professional review recorded.",
    },
}


def get_review_status_badge(status: str | None) -> str:
    """Return a formatted markdown badge string for a review status."""
    if not status:
        return "`⚪ [NOT REVIEWED]`"
    normalized = status.strip().upper()
    cfg = REVIEW_STATUS_CONFIG.get(normalized)
    if cfg:
        return f"`{cfg['icon']} [{cfg['label']}]`"
    return f"`⚪ [{normalized}]`"


# ── Alert Status Badges ──────────────────────────────────────────────────────

ALERT_STATUS_CONFIG: dict[str, dict[str, str]] = {
    "NOT_TRIGGERED": {
        "label": "NOT TRIGGERED",
        "icon": "⚪",
        "color": "#6b7280",
        "description": "Risk score did not reach critical alert thresholds.",
    },
    "TRIGGERED": {
        "label": "TRIGGERED",
        "icon": "⚡",
        "color": "#ea580c",
        "description": "Threshold reached; alert generation queued.",
    },
    "SENT": {
        "label": "ALERT SENT",
        "icon": "📤",
        "color": "#2563eb",
        "description": "Emergency notification dispatched successfully.",
    },
    "FAILED": {
        "label": "ALERT FAILED",
        "icon": "⚠️",
        "color": "#dc2626",
        "description": "Notification dispatch encountered a transmission failure.",
    },
}


def get_alert_status_badge(status: str | None) -> str:
    """Return a formatted markdown badge string for an alert status."""
    if not status:
        return "`⚪ [NOT TRIGGERED]`"
    normalized = status.strip().upper()
    cfg = ALERT_STATUS_CONFIG.get(normalized)
    if cfg:
        return f"`{cfg['icon']} [{cfg['label']}]`"
    return f"`⚪ [{normalized}]`"


# ── Priority Badges (Phase 13) ───────────────────────────────────────────────

PRIORITY_CONFIG: dict[str, dict[str, str]] = {
    "HIGH": {
        "label": "HIGH PRIORITY",
        "icon": "🔴",
        "color": "#dc2626",
    },
    "MEDIUM": {
        "label": "MEDIUM PRIORITY",
        "icon": "🟡",
        "color": "#d97706",
    },
    "LOW": {
        "label": "LOW PRIORITY",
        "icon": "🟢",
        "color": "#16a34a",
    },
    "INFO": {
        "label": "INFORMATIONAL",
        "icon": "ℹ️",
        "color": "#2563eb",
    },
}


def get_priority_badge(priority: str | None) -> str:
    """Return a formatted markdown badge string for a recommendation priority."""
    if not priority:
        return "`ℹ️ [INFO]`"
    normalized = priority.strip().upper()
    cfg = PRIORITY_CONFIG.get(normalized)
    if cfg:
        return f"`{cfg['icon']} [{cfg['label']}]`"
    return f"`ℹ️ [{normalized}]`"


def render_badge(badge_markdown: str) -> None:
    """Render a badge markdown string inside Streamlit."""
    st.markdown(badge_markdown)

