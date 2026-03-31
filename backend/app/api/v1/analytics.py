from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    CoachingReport, ScoreTrendReport, ApplicationFunnel, DashboardSummary,
)
from app.services.coaching_service import generate_coaching_tips
from app.services.analytics_service import (
    application_funnel, score_trend, dashboard_summary,
)
from app.services.cv_service import get_cv_by_id
from app.services.job_service import get_job_by_id

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Top-level stats for the user's home dashboard."""
    return dashboard_summary(db, current_user.id)


@router.get("/funnel", response_model=ApplicationFunnel)
def get_application_funnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Application funnel: counts and conversion rates per status."""
    return application_funnel(db, current_user.id)


@router.get("/score-trend/{cv_id}", response_model=ScoreTrendReport)
def get_score_trend(
    cv_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Match score trend across all tailored versions of a CV.
    Shows how the score improves with each tailoring iteration.
    """
    cv = get_cv_by_id(db, cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    return score_trend(db, current_user.id, cv_id)


@router.post("/coaching", response_model=CoachingReport)
def get_coaching(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate coaching tips for a CV against a job.
    Body: {"cv_id": "...", "job_id": "..."}
    """
    cv_id = payload.get("cv_id")
    job_id = payload.get("job_id")
    if not cv_id or not job_id:
        raise HTTPException(status_code=422, detail="cv_id and job_id are required.")

    try:
        cv_uuid = uuid.UUID(str(cv_id))
        job_uuid = uuid.UUID(str(job_id))
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format.")

    cv = get_cv_by_id(db, cv_uuid, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    if not cv.parsed_data:
        raise HTTPException(status_code=400, detail="CV must be parsed before coaching.")

    job = get_job_by_id(db, job_uuid, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    return generate_coaching_tips(cv.parsed_data, job.description)
