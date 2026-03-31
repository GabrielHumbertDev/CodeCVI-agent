"""
Audit logging service.
Call log_action() from any endpoint to record a GDPR-compliant audit trail.
"""
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id: uuid.UUID,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    detail: Optional[dict] = None,
) -> None:
    """
    Record an audit log entry. Silently ignores errors so logging
    never breaks the main request flow.
    """
    try:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            detail=detail or {},
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
