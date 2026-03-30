from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.job import JobCreate, JobOut, JobListOut
from app.services.job_service import create_job, get_jobs_by_user, get_job_by_id, delete_job
import uuid

router = APIRouter()


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job_endpoint(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    return create_job(
        db=db,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        company=payload.company,
    )


@router.get("", response_model=JobListOut)
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    jobs = get_jobs_by_user(db, current_user.id)
    return JobListOut(jobs=jobs, total=len(jobs))


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_endpoint(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    delete_job(db, job)
