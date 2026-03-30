from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cv import CVVersion
import uuid


def create_cv_version(
    db: Session,
    cv_id: uuid.UUID,
    job_id: uuid.UUID,
    tailored_data: dict,
    validation_passed: bool,
) -> CVVersion:
    # Get next version number for this CV
    existing_count = db.query(CVVersion).filter(CVVersion.cv_id == cv_id).count()
    version_number = existing_count + 1

    version = CVVersion(
        cv_id=cv_id,
        job_id=job_id,
        version_number=version_number,
        tailored_data=tailored_data,
        validation_passed=validation_passed,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def get_versions_by_cv(db: Session, cv_id: uuid.UUID) -> List[CVVersion]:
    return (
        db.query(CVVersion)
        .filter(CVVersion.cv_id == cv_id)
        .order_by(CVVersion.version_number.desc())
        .all()
    )


def get_version_by_id(db: Session, version_id: uuid.UUID) -> Optional[CVVersion]:
    return db.query(CVVersion).filter(CVVersion.id == version_id).first()
