from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email, User.is_deleted == False).first()


def get_user_by_id(db: Session, user_id) -> Optional[User]:
    return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    role: str = UserRole.USER,
    status: str = UserStatus.PENDING,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
        status=status,
        # is_active mirrors status for backward compat
        is_active=(status == UserStatus.ACTIVE),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_last_login(db: Session, user: User) -> None:
    user.last_login_at = datetime.utcnow()
    db.commit()
