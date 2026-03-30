from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.match import MatchRequest, MatchResult
from app.services.cv_service import get_cv_by_id
from app.services.job_service import get_job_by_id
from app.services.match_engine import score_match

router = APIRouter()


@router.post("", response_model=MatchResult)
def match_cv_to_job(
    payload: MatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cv = get_cv_by_id(db, payload.cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")

    if cv.parse_status != "done" or not cv.parsed_data:
        raise HTTPException(
            status_code=400,
            detail="CV has not been parsed yet. Please wait for parsing to complete.",
        )

    job = get_job_by_id(db, payload.job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    result = score_match(cv.parsed_data, job.description)

    return MatchResult(
        cv_id=payload.cv_id,
        job_id=payload.job_id,
        **result,
    )
