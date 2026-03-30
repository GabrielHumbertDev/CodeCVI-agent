from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models.base import Base


class CV(Base):
    __tablename__ = "cvs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf or docx
    parsed_data = Column(JSONB, nullable=True)       # structured CV JSON
    parse_status = Column(String(20), default="pending", nullable=False)  # pending, done, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="cvs")
    versions = relationship("CVVersion", back_populates="cv", cascade="all, delete-orphan")


class CVVersion(Base):
    __tablename__ = "cv_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv_id = Column(UUID(as_uuid=True), ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    version_number = Column(Integer, nullable=False, default=1)
    tailored_data = Column(JSONB, nullable=False)   # AI-tailored CV JSON
    validation_passed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cv = relationship("CV", back_populates="versions")
    job = relationship("Job", back_populates="cv_versions")
    applications = relationship("Application", back_populates="cv_version")
