from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from app.models.application import Application


def create_application(
    db: Session,
    user_id: uuid.UUID,
    job_id: uuid.UUID,
    cv_version_id: Optional[uuid.UUID],
    status: str,
    notes: Optional[str],
) -> Application:
    app = Application(
        user_id=user_id,
        job_id=job_id,
        cv_version_id=cv_version_id,
        status=status,
        notes=notes,
        applied_at=datetime.utcnow() if status == "applied" else None,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def get_applications(
    db: Session,
    user_id: uuid.UUID,
    status: Optional[str] = None,
) -> list[Application]:
    q = db.query(Application).filter(Application.user_id == user_id)
    if status:
        q = q.filter(Application.status == status)
    return q.order_by(Application.created_at.desc()).all()


def get_application_by_id(
    db: Session,
    application_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Optional[Application]:
    return (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == user_id)
        .first()
    )


def update_application(
    db: Session,
    application: Application,
    status: Optional[str],
    notes: Optional[str],
    applied_at: Optional[datetime],
) -> Application:
    if status is not None:
        application.status = status
        # Auto-set applied_at when status moves to "applied"
        if status == "applied" and application.applied_at is None:
            application.applied_at = datetime.utcnow()
    if notes is not None:
        application.notes = notes
    if applied_at is not None:
        application.applied_at = applied_at

    db.commit()
    db.refresh(application)
    return application


def delete_application(db: Session, application: Application) -> None:
    db.delete(application)
    db.commit()
