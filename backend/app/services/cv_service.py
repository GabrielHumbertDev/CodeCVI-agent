from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cv import CV
import uuid


def create_cv_record(
    db: Session,
    user_id: uuid.UUID,
    filename: str,
    file_path: str,
    file_type: str,
) -> CV:
    cv = CV(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        parse_status="pending",
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return cv


def get_cvs_by_user(db: Session, user_id: uuid.UUID) -> List[CV]:
    return db.query(CV).filter(CV.user_id == user_id).order_by(CV.created_at.desc()).all()


def get_cv_by_id(db: Session, cv_id: uuid.UUID, user_id: uuid.UUID) -> Optional[CV]:
    return db.query(CV).filter(CV.id == cv_id, CV.user_id == user_id).first()


def delete_cv_record(db: Session, cv: CV) -> None:
    db.delete(cv)
    db.commit()
