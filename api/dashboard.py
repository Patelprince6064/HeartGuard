"""Dashboard router for HeartGuard API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.deps import CurrentUser, get_current_user
from src.analytics.analytics_service import AnalyticsService
from src.analytics.history_service import HistoryService
from src.analytics.trend_service import TrendService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class DashboardResponse(BaseModel):
    statistics: dict[str, Any]
    latest_assessment: dict[str, Any] | None
    recent_assessments: list[dict[str, Any]]
    trends: list[dict[str, Any]]


@router.get("", response_model=DashboardResponse)
async def get_dashboard(current_user: CurrentUser = Depends(get_current_user)):
    stats = AnalyticsService.calculate_user_statistics(user_id=current_user.user_id)

    latest = HistoryService.get_latest_assessment(user_id=current_user.user_id)
    latest_dict = latest.to_dict() if latest else None

    recent = AnalyticsService.get_user_recent_assessments(
        user_id=current_user.user_id,
        limit=5,
    )

    trends = TrendService.get_risk_trends(user_id=current_user.user_id)

    return DashboardResponse(
        statistics=stats,
        latest_assessment=latest_dict,
        recent_assessments=recent,
        trends=trends,
    )
