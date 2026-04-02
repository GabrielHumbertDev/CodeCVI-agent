"""
Admin service — user lifecycle management.
All mutations go through here so business rules are enforced consistently.
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from app.models.user import User, UserStatus, UserRole
from app.core.security import hash_password


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def list_users(
    db: Session,
    status: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
    include_deleted: bool = False,
) -> list[User]:
    q = db.query(User)
    if not include_deleted:
        q = q.filter(User.is_deleted == False)
    if status:
        q = q.filter(User.status == status)
    if role:
        q = q.filter(User.role == role)
    if search:
        term = f"%{search.lower()}%"
        q = q.filter(
            (User.email.ilike(term)) | (User.full_name.ilike(term))
        )
    return q.order_by(User.created_at.desc()).all()


def get_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

def approve_user(db: Session, target: User, admin: User) -> User:
    if target.status not in (UserStatus.PENDING,):
        raise ValueError(f"Cannot approve a user with status '{target.status}'.")
    target.status = UserStatus.ACTIVE
    target.is_active = True
    target.approved_at = datetime.utcnow()
    target.approved_by = admin.id
    db.commit()
    db.refresh(target)
    return target


def pause_user(db: Session, target: User, admin: User, reason: Optional[str] = None) -> User:
    if target.status != UserStatus.ACTIVE:
        raise ValueError(f"Cannot pause a user with status '{target.status}'.")
    if str(target.id) == str(admin.id):
        raise ValueError("Admins cannot pause themselves.")
    target.status = UserStatus.PAUSED
    target.is_active = False
    target.paused_at = datetime.utcnow()
    target.pause_reason = reason
    db.commit()
    db.refresh(target)
    return target


def resume_user(db: Session, target: User, admin: User) -> User:
    if target.status != UserStatus.PAUSED:
        raise ValueError(f"Cannot resume a user with status '{target.status}'.")
    target.status = UserStatus.ACTIVE
    target.is_active = True
    target.paused_at = None
    target.pause_reason = None
    db.commit()
    db.refresh(target)
    return target


def disable_user(db: Session, target: User, admin: User) -> User:
    if target.status == UserStatus.DISABLED:
        raise ValueError("User is already disabled.")
    if str(target.id) == str(admin.id):
        raise ValueError("Admins cannot disable themselves.")
    target.status = UserStatus.DISABLED
    target.is_active = False
    db.commit()
    db.refresh(target)
    return target


def soft_delete_user(db: Session, target: User, admin: User) -> User:
    if str(target.id) == str(admin.id):
        raise ValueError("Admins cannot delete themselves.")
    target.is_deleted = True
    target.is_active = False
    target.status = UserStatus.DISABLED
    db.commit()
    db.refresh(target)
    return target


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

def edit_user(
    db: Session,
    target: User,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
) -> User:
    if full_name is not None:
        target.full_name = full_name
    if email is not None:
        target.email = email
    if role is not None:
        if role not in (UserRole.USER, UserRole.ADMIN):
            raise ValueError(f"Invalid role '{role}'.")
        target.role = role
    target.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(target)
    return target
