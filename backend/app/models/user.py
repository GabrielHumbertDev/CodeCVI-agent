from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models.base import Base

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class UserRole:
    USER = "user"
    ADMIN = "admin"

class UserStatus:
    PENDING = "pending_approval"
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Legacy field — kept for backward compatibility, mirrors status==active
    is_active = Column(Boolean, default=True, nullable=False)

    # --- Admin fields ---
    role = Column(String(20), default=UserRole.USER, nullable=False)
    status = Column(String(30), default=UserStatus.PENDING, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)   # admin user id
    paused_at = Column(DateTime, nullable=True)
    pause_reason = Column(String(500), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # --- GDPR fields ---
    gdpr_consent = Column(Boolean, default=False, nullable=False)
    gdpr_consent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    cvs = relationship("CV", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
