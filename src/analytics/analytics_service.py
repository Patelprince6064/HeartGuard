"""Analytics Service for HeartGuard patient summaries and admin aggregation (Phase 10).

Calculates patient-level metrics (total assessments, averages, category distributions)
and privacy-safe system-wide aggregate statistics for administrators.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any

from config.settings import ASSESSMENTS_DB_PATH
from src.analytics.history_service import HistoryService, _get_connection


class AnalyticsService:
    """Provides statistical aggregations for patient dashboards and administrator reports."""

    @staticmethod
    def calculate_user_statistics(
        user_id: int,
        db_path: Path | None = None,
    ) -> dict[str, Any]:
        """Calculate high-level summary metrics for an individual patient.

        Args:
            user_id: Authenticated user ID.
            db_path: SQLite DB path override.

        Returns:
            dict with total_assessments, latest_risk, average_risk, critical_count.
        """
        assessments = HistoryService.get_user_assessments(
            user_id=user_id, sort_order="desc", limit=None, db_path=db_path
        )

        total = len(assessments)
        if total == 0:
            return {
                "total_assessments": 0,
                "latest_risk": None,
                "latest_category": None,
                "latest_alert_status": None,
                "average_overall_risk": None,
                "critical_count": 0,
            }

        latest = assessments[0]
        avg_risk = round(sum(a.overall_risk for a in assessments) / total, 2)
        critical_count = sum(
            1 for a in assessments if "CRITICAL" in a.risk_category.upper()
        )

        return {
            "total_assessments": total,
            "latest_risk": latest.overall_risk,
            "latest_category": latest.risk_category,
            "latest_alert_status": latest.alert_status,
            "average_overall_risk": avg_risk,
            "critical_count": critical_count,
        }

    @staticmethod
    def get_category_distribution(
        user_id: int,
        db_path: Path | None = None,
    ) -> dict[str, int]:
        """Compute the count of assessments per risk category for the user."""
        with _get_connection(db_path) as conn:
            rows = conn.execute(
                """
                SELECT risk_category, COUNT(*) as count
                FROM assessments
                WHERE user_id = ?
                GROUP BY risk_category
                ORDER BY count DESC;
                """,
                (user_id,),
            ).fetchall()
            return {row["risk_category"]: int(row["count"]) for row in rows}

    @staticmethod
    def get_admin_aggregated_analytics(
        db_path: Path | None = None,
    ) -> dict[str, Any]:
        """Aggregate system-wide assessment metrics for admin dashboards.

        Privacy guarantee: Returns ONLY aggregated counts and distributions.
        Does NOT expose patient names, emails, raw text, or individual records.
        """
        with _get_connection(db_path) as conn:
            # Total assessments and distinct assessed patients
            overview_row = conn.execute(
                """
                SELECT COUNT(*) as total_assessments,
                       COUNT(DISTINCT user_id) as active_patients,
                       AVG(overall_risk) as avg_risk
                FROM assessments;
                """
            ).fetchone()

            total_assessments = int(overview_row["total_assessments"]) if overview_row else 0
            active_patients = int(overview_row["active_patients"]) if overview_row else 0
            avg_risk = (
                round(float(overview_row["avg_risk"]), 2)
                if overview_row and overview_row["avg_risk"] is not None
                else 0.0
            )

            # Category distribution across entire application
            cat_rows = conn.execute(
                """
                SELECT risk_category, COUNT(*) as count
                FROM assessments
                GROUP BY risk_category
                ORDER BY count DESC;
                """
            ).fetchall()
            cat_dist = {r["risk_category"]: int(r["count"]) for r in cat_rows}

            # Model version usage counts (for model traceability)
            model_rows = conn.execute(
                """
                SELECT model_version, COUNT(*) as count
                FROM assessments
                GROUP BY model_version
                ORDER BY count DESC;
                """
            ).fetchall()
            model_dist = {r["model_version"]: int(r["count"]) for r in model_rows}

            # Alert status outcomes
            alert_rows = conn.execute(
                """
                SELECT alert_status, COUNT(*) as count
                FROM assessments
                GROUP BY alert_status
                ORDER BY count DESC;
                """
            ).fetchall()
            alert_dist = {r["alert_status"]: int(r["count"]) for r in alert_rows}

            return {
                "total_assessments": total_assessments,
                "active_patients": active_patients,
                "average_system_risk": avg_risk,
                "category_distribution": cat_dist,
                "model_version_distribution": model_dist,
                "alert_status_distribution": alert_dist,
            }
