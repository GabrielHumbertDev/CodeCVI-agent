"""
GDPR service: data export and account erasure.
"""
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.user import User
from app.models.cv import CV, CVVersion
from app.models.job import Job
from app.models.application import Application
from app.models.cover_letter import CoverLetter
from app.models.audit_log import AuditLog
from app.core.security import verify_password


# ---------------------------------------------------------------------------
# Data export (Right of Access — GDPR Art. 15)
# ---------------------------------------------------------------------------

def export_user_data(db: Session, user: User) -> dict:
    """Return all personal data held for this user as a structured dict."""

    cvs = db.query(CV).filter(CV.user_id == user.id).all()
    jobs = db.query(Job).filter(Job.user_id == user.id).all()
    applications = db.query(Application).filter(Application.user_id == user.id).all()
    cover_letters = db.query(CoverLetter).filter(CoverLetter.user_id == user.id).all()
    audit_logs = db.query(AuditLog).filter(AuditLog.user_id == user.id).all()

    def _cv_version_data(cv: CV) -> list:
        return [
            {
                "id": str(v.id),
                "job_id": str(v.job_id) if v.job_id else None,
                "version_number": v.version_number,
                "validation_passed": v.validation_passed,
                "tailored_data": v.tailored_data,
                "created_at": v.created_at.isoformat(),
            }
            for v in cv.versions
        ]

    return {
        "export_generated_at": datetime.utcnow().isoformat() + "Z",
        "profile": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "gdpr_consent": user.gdpr_consent,
            "gdpr_consent_at": user.gdpr_consent_at.isoformat() if user.gdpr_consent_at else None,
            "created_at": user.created_at.isoformat(),
        },
        "cvs": [
            {
                "id": str(cv.id),
                "filename": cv.filename,
                "file_type": cv.file_type,
                "parse_status": cv.parse_status,
                "parsed_data": cv.parsed_data,
                "created_at": cv.created_at.isoformat(),
                "versions": _cv_version_data(cv),
            }
            for cv in cvs
        ],
        "jobs": [
            {
                "id": str(j.id),
                "title": j.title,
                "company": j.company,
                "description": j.description,
                "created_at": j.created_at.isoformat(),
            }
            for j in jobs
        ],
        "applications": [
            {
                "id": str(a.id),
                "job_id": str(a.job_id),
                "cv_version_id": str(a.cv_version_id) if a.cv_version_id else None,
                "status": a.status,
                "notes": a.notes,
                "applied_at": a.applied_at.isoformat() if a.applied_at else None,
                "created_at": a.created_at.isoformat(),
            }
            for a in applications
        ],
        "cover_letters": [
            {
                "id": str(cl.id),
                "job_id": str(cl.job_id),
                "version_number": cl.version_number,
                "content": cl.content,
                "created_at": cl.created_at.isoformat(),
            }
            for cl in cover_letters
        ],
        "audit_log": [
            {
                "id": str(log.id),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "detail": log.detail,
                "created_at": log.created_at.isoformat(),
            }
            for log in audit_logs
        ],
    }


# ---------------------------------------------------------------------------
# Account erasure (Right to Erasure — GDPR Art. 17)
# ---------------------------------------------------------------------------

def erase_user_account(db: Session, user: User, password: str) -> bool:
    """
    Verify password then permanently delete the user and all their data.
    Returns True on success, False if password is wrong.
    """
    if not verify_password(password, user.hashed_password):
        return False

    db.delete(user)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Consent management
# ---------------------------------------------------------------------------

def update_consent(db: Session, user: User, consent: bool) -> User:
    user.gdpr_consent = consent
    user.gdpr_consent_at = datetime.utcnow() if consent else None
    db.commit()
    db.refresh(user)
    return user
