from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.gdpr_service import export_user_data, erase_user_account, update_consent
from app.services.audit_service import log_action

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ConsentUpdate(BaseModel):
    consent: bool


class EraseRequest(BaseModel):
    password: str
    confirm: str   # must equal "DELETE MY ACCOUNT"


class AuditLogOut(BaseModel):
    id: uuid.UUID
    action: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    detail: Optional[dict]
    created_at: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/export")
def export_my_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Right of Access (GDPR Art. 15) — download all your personal data."""
    log_action(db, current_user.id, "gdpr.export", "user", str(current_user.id))
    data = export_user_data(db, current_user)
    return JSONResponse(content=data)


@router.post("/consent")
def update_gdpr_consent(
    payload: ConsentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record or withdraw GDPR consent."""
    user = update_consent(db, current_user, payload.consent)
    log_action(
        db, current_user.id, "gdpr.consent_updated", "user", str(current_user.id),
        {"consent": payload.consent}
    )
    return {
        "gdpr_consent": user.gdpr_consent,
        "gdpr_consent_at": user.gdpr_consent_at.isoformat() if user.gdpr_consent_at else None,
    }


@router.get("/audit-log", response_model=list[AuditLogOut])
def get_my_audit_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """View your personal audit trail (all actions recorded on your account)."""
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    return [
        AuditLogOut(
            id=log.id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            detail=log.detail,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.delete("/me", status_code=status.HTTP_200_OK)
def erase_my_account(
    payload: EraseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Right to Erasure (GDPR Art. 17) — permanently delete your account and all data.
    Requires password confirmation and the phrase 'DELETE MY ACCOUNT'.
    """
    if payload.confirm != "DELETE MY ACCOUNT":
        raise HTTPException(
            status_code=400,
            detail="Confirmation phrase must be exactly: DELETE MY ACCOUNT",
        )

    success = erase_user_account(db, current_user, payload.password)
    if not success:
        raise HTTPException(status_code=401, detail="Incorrect password.")

    return {"detail": "Your account and all associated data have been permanently deleted."}
