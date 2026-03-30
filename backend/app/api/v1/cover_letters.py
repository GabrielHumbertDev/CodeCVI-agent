from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterUpdate, CoverLetterOut
from app.services.cv_service import get_cv_by_id
from app.services.job_service import get_job_by_id
from app.services.cover_letter_generator import generate_cover_letter
from app.services.cover_letter_service import (
    create_cover_letter, get_cover_letters_by_job,
    get_cover_letter_by_id, update_cover_letter_content,
)
import uuid

router = APIRouter()


@router.post("", response_model=CoverLetterOut, status_code=status.HTTP_201_CREATED)
async def generate_cover_letter_endpoint(
    payload: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cv = get_cv_by_id(db, payload.cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    if cv.parse_status != "done" or not cv.parsed_data:
        raise HTTPException(status_code=400, detail="CV must be parsed before generating a cover letter.")

    job = get_job_by_id(db, payload.job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    try:
        content = await generate_cover_letter(
            cv_data=cv.parsed_data,
            job_description=job.description,
            company=job.company or "",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    cl = create_cover_letter(
        db=db,
        user_id=current_user.id,
        job_id=job.id,
        content=content,
    )
    return cl


@router.get("/job/{job_id}", response_model=list[CoverLetterOut])
def list_cover_letters(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return get_cover_letters_by_job(db, job_id, current_user.id)


@router.put("/{cl_id}", response_model=CoverLetterOut)
def update_cover_letter(
    cl_id: uuid.UUID,
    payload: CoverLetterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cl = get_cover_letter_by_id(db, cl_id, current_user.id)
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found.")
    return update_cover_letter_content(db, cl, payload.content)
