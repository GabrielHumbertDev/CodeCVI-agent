from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.cv_version import TailorRequest, CVVersionOut
from app.services.cv_service import get_cv_by_id
from app.services.job_service import get_job_by_id
from app.services.cv_tailor import tailor_cv
from app.services.cv_version_service import create_cv_version, get_versions_by_cv
import uuid

router = APIRouter()


@router.post("", response_model=CVVersionOut, status_code=status.HTTP_201_CREATED)
async def tailor_cv_endpoint(
    payload: TailorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cv = get_cv_by_id(db, payload.cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    if cv.parse_status != "done" or not cv.parsed_data:
        raise HTTPException(status_code=400, detail="CV must be parsed before tailoring.")

    job = get_job_by_id(db, payload.job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    try:
        tailored_data, validation_passed, violations = await tailor_cv(
            cv.parsed_data, job.description
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    version = create_cv_version(
        db=db,
        cv_id=cv.id,
        job_id=job.id,
        tailored_data=tailored_data,
        validation_passed=validation_passed,
    )

    return version


@router.get("/{cv_id}/versions", response_model=list[CVVersionOut])
def list_cv_versions(
    cv_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cv = get_cv_by_id(db, cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    return get_versions_by_cv(db, cv_id)


@router.get("/versions/{version_id}", response_model=CVVersionOut)
def get_cv_version(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    version = get_version_by_id(db, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="CV version not found.")
    # Ensure version belongs to the current user via the parent CV
    cv = get_cv_by_id(db, version.cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV version not found.")
    return version
