from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.api.v1.deps import require_admin
from app.models.user import User
from app.schemas.user import AdminUserOut, AdminUserEdit, AdminPauseRequest
from app.services import admin_service
from app.services.audit_service import log_action

router = APIRouter()


def _get_target(db: Session, user_id: uuid.UUID) -> User:
    """Fetch target user or raise 404."""
    user = admin_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


def _handle(fn, *args, **kwargs):
    """Run a service call and convert ValueError to 400."""
    try:
        return fn(*args, **kwargs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# List & detail
# ---------------------------------------------------------------------------

@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all users with optional filters."""
    return admin_service.list_users(db, status=status, role=role, search=search, include_deleted=include_deleted)


@router.get("/users/{user_id}", response_model=AdminUserOut)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return _get_target(db, user_id)


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

@router.put("/users/{user_id}", response_model=AdminUserOut)
def edit_user(
    user_id: uuid.UUID,
    payload: AdminUserEdit,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    target = _get_target(db, user_id)
    updated = _handle(
        admin_service.edit_user, db, target,
        full_name=payload.full_name,
        email=str(payload.email) if payload.email else None,
        role=payload.role,
    )
    log_action(db, admin.id, "admin.user.edit", "user", str(user_id),
               {"changed_by": str(admin.id)})
    return updated


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

@router.post("/users/{user_id}/approve", response_model=AdminUserOut)
def approve_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    target = _get_target(db, user_id)
    updated = _handle(admin_service.approve_user, db, target, admin)
    log_action(db, admin.id, "admin.user.approve", "user", str(user_id),
               {"approved_by": str(admin.id)})
    return updated


@router.post("/users/{user_id}/pause", response_model=AdminUserOut)
def pause_user(
    user_id: uuid.UUID,
    payload: AdminPauseRequest = AdminPauseRequest(),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    target = _get_target(db, user_id)
    updated = _handle(admin_service.pause_user, db, target, admin, reason=payload.reason)
    log_action(db, admin.id, "admin.user.pause", "user", str(user_id),
               {"reason": payload.reason, "by": str(admin.id)})
    return updated


@router.post("/users/{user_id}/resume", response_model=AdminUserOut)
def resume_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    target = _get_target(db, user_id)
    updated = _handle(admin_service.resume_user, db, target, admin)
    log_action(db, admin.id, "admin.user.resume", "user", str(user_id),
               {"by": str(admin.id)})
    return updated


@router.post("/users/{user_id}/disable", response_model=AdminUserOut)
def disable_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    target = _get_target(db, user_id)
    updated = _handle(admin_service.disable_user, db, target, admin)
    log_action(db, admin.id, "admin.user.disable", "user", str(user_id),
               {"by": str(admin.id)})
    return updated


@router.delete("/users/{user_id}", response_model=AdminUserOut)
def soft_delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    target = _get_target(db, user_id)
    updated = _handle(admin_service.soft_delete_user, db, target, admin)
    log_action(db, admin.id, "admin.user.delete", "user", str(user_id),
               {"by": str(admin.id)})
    return updated
