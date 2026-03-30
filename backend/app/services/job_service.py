from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.job import Job
import uuid


def create_job(
    db: Session,
    user_id: uuid.UUID,
    title: str,
    description: str,
    company: Optional[str] = None,
) -> Job:
    job = Job(
        user_id=user_id,
        title=title,
        company=company,
        description=description,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_jobs_by_user(db: Session, user_id: uuid.UUID) -> List[Job]:
    return db.query(Job).filter(Job.user_id == user_id).order_by(Job.created_at.desc()).all()


def get_job_by_id(db: Session, job_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Job]:
    return db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()


def delete_job(db: Session, job: Job) -> None:
    db.delete(job)
    db.commit()
