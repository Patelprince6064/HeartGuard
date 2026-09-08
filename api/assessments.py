"""Assessment router for HeartGuard API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.deps import CurrentUser, get_current_user, require_role
from src.alerts.alert_manager import AlertManager
from src.analytics.history_service import HistoryService
from src.risk_engine.multimodal_risk import MultimodalRiskEngine

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


class AssessmentCreateRequest(BaseModel):
    clinical_data: dict[str, Any]
    lifestyle_text: str


class AssessmentResponse(BaseModel):
    id: int | None
    assessment_id: str
    user_id: int
    created_at: str
    clinical_risk: float
    lifestyle_risk: float
    overall_risk: float
    risk_category: str
    recommendation: str
    model_version: str
    narrative_summary: str
    alert_status: str


def _assessment_to_response(asmt) -> AssessmentResponse:
    return AssessmentResponse(
        id=asmt.id,
        assessment_id=asmt.assessment_id,
        user_id=asmt.user_id,
        created_at=asmt.created_at,
        clinical_risk=asmt.clinical_risk,
        lifestyle_risk=asmt.lifestyle_risk,
        overall_risk=asmt.overall_risk,
        risk_category=asmt.risk_category,
        recommendation=asmt.recommendation,
        model_version=asmt.model_version,
        narrative_summary=asmt.narrative_summary,
        alert_status=asmt.alert_status,
    )


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    body: AssessmentCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        engine = MultimodalRiskEngine()
        result = engine.assess(
            clinical_data=body.clinical_data,
            lifestyle_text=body.lifestyle_text,
        )

        alert_manager = AlertManager()
        alert_result = alert_manager.process_risk_result(
            risk_result=result,
            assessment_id=None,
        )

        asmt = HistoryService.save_assessment(
            user_id=current_user.user_id,
            multimodal_result=result,
            alert_status=alert_result.get("notification_status", "NOT_TRIGGERED"),
        )

        return _assessment_to_response(asmt)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assessment failed")


@router.get("", response_model=list[AssessmentResponse])
async def list_assessments(current_user: CurrentUser = Depends(get_current_user)):
    if current_user.role == "ADMIN":
        from src.analytics.history_service import _get_connection, _row_to_assessment
        with _get_connection() as conn:
            rows = conn.execute("SELECT * FROM assessments ORDER BY created_at DESC LIMIT 100").fetchall()
            return [_assessment_to_response(_row_to_assessment(r)) for r in rows]

    assessments = HistoryService.get_user_assessments(
        user_id=current_user.user_id,
        sort_order="desc",
        limit=50,
    )
    return [_assessment_to_response(a) for a in assessments]


@router.get("/latest", response_model=AssessmentResponse)
async def get_latest_assessment(current_user: CurrentUser = Depends(get_current_user)):
    asmt = HistoryService.get_latest_assessment(user_id=current_user.user_id)
    if asmt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No assessments found")
    return _assessment_to_response(asmt)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.role in ("ADMIN", "REVIEWER"):
        asmt = HistoryService.get_assessment_by_id(assessment_id, user_id=None)
    else:
        asmt = HistoryService.get_assessment_by_id(assessment_id, user_id=current_user.user_id)

    if asmt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if current_user.role == "PATIENT" and asmt.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return _assessment_to_response(asmt)
