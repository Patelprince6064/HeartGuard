"""Tabular formatting and display helpers for HeartGuard (Phase 12).

Provides accessible, responsive table presentations for:
  - Patient recent assessments
  - Reviewer assessment queues
  - User accounts (Admin)
  - Security audit events (Admin)
"""

from __future__ import annotations

from typing import Any
import pandas as pd
import streamlit as st

from src.ui.badges import (
    get_alert_status_badge,
    get_risk_category_badge,
    get_review_status_badge,
)
from src.ui.cards import format_risk_percentage


def render_recent_assessments_table(
    assessments: list[dict[str, Any]],
    limit: int = 5,
    show_full_link: bool = True,
) -> None:
    """Render a clean tabular view of the patient's recent assessments."""
    if not assessments:
        st.info("No assessments to display.")
        return

    display_rows = []
    for a in assessments[:limit]:
        created = str(a.get("created_at", ""))[:10]
        aid = str(a.get("assessment_id", ""))
        overall = format_risk_percentage(a.get("overall_risk"))
        cat = str(a.get("risk_category", "N/A"))
        rev_status = str(a.get("review_status", "PENDING"))
        alert_status = str(a.get("alert_status", "NOT_TRIGGERED"))

        display_rows.append(
            {
                "Date": created,
                "Assessment ID": aid,
                "Overall Risk": overall,
                "Category": cat,
                "Review Status": rev_status,
                "Alert Outcome": alert_status,
            }
        )

    df = pd.DataFrame(display_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if show_full_link and len(assessments) > limit:
        st.caption(f"Showing {limit} most recent of {len(assessments)} total assessments.")
        st.page_link(
            "pages/history.py",
            label=f"📜 View All {len(assessments)} Assessments in History →",
        )


def render_reviewer_queue_table(queue_items: list[dict[str, Any]]) -> None:
    """Render a formatted queue table for authorized reviewers."""
    if not queue_items:
        st.info("No assessments currently in the queue.")
        return

    rows = []
    for item in queue_items:
        aid = str(item.get("assessment_id", ""))
        date_str = str(item.get("created_at", ""))[:10]
        risk_str = format_risk_percentage(item.get("overall_risk"))
        cat = str(item.get("risk_category", ""))
        rev_status = str(item.get("review_status", "PENDING"))
        urgency = "⚡ High Urgency" if item.get("urgency_flag") else "Normal"
        follow_up = "⚠️ Required" if item.get("follow_up_required") else "No"

        rows.append(
            {
                "Assessment ID": aid,
                "Date": date_str,
                "Risk Score": risk_str,
                "Category": cat,
                "Review Status": rev_status,
                "Priority": urgency,
                "Follow-Up": follow_up,
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
