from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cover_letter import CoverLetter
import uuid


def create_cover_letter(
    db: Session,
    user_id: uuid.UUID,
    job_id: uuid.UUID,
    content: str,
) -> CoverLetter:
    existing_count = (
        db.query(CoverLetter)
        .filter(CoverLetter.job_id == job_id, CoverLetter.user_id == user_id)
        .count()
    )
    version_number = existing_count + 1

    cl = CoverLetter(
        user_id=user_id,
        job_id=job_id,
        content=content,
        version_number=version_number,
    )
    db.add(cl)
    db.commit()
    db.refresh(cl)
    return cl


def get_cover_letters_by_job(
    db: Session, job_id: uuid.UUID, user_id: uuid.UUID
) -> List[CoverLetter]:
    return (
        db.query(CoverLetter)
        .filter(CoverLetter.job_id == job_id, CoverLetter.user_id == user_id)
        .order_by(CoverLetter.version_number.desc())
        .all()
    )


def get_cover_letter_by_id(
    db: Session, cl_id: uuid.UUID, user_id: uuid.UUID
) -> Optional[CoverLetter]:
    return (
        db.query(CoverLetter)
        .filter(CoverLetter.id == cl_id, CoverLetter.user_id == user_id)
        .first()
    )


def update_cover_letter_content(
    db: Session, cl: CoverLetter, content: str
) -> CoverLetter:
    cl.content = content
    db.commit()
    db.refresh(cl)
    return cl
