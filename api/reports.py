"""Reports router for HeartGuard API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import io

from api.deps import CurrentUser, get_current_user
from src.reports.report_generator import ReportGenerator

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/{assessment_id}/generate")
async def generate_report(
    assessment_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        pdf_bytes = ReportGenerator.generate_assessment_report(
            assessment_id=assessment_id,
            user_id=current_user.user_id,
        )
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="HeartGuard-Report-{assessment_id}.pdf"'
            },
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{assessment_id}/download")
async def download_report(
    assessment_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        pdf_bytes = ReportGenerator.generate_assessment_report(
            assessment_id=assessment_id,
            user_id=current_user.user_id,
        )
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="HeartGuard-Report-{assessment_id}.pdf"'
            },
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
