from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import uuid

VALID_STATUSES = {"draft", "applied", "interview", "offer", "rejected", "withdrawn"}


class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    cv_version_id: Optional[uuid.UUID] = None
    status: str = "draft"
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
        return v


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
        return v


class ApplicationOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    cv_version_id: Optional[uuid.UUID]
    status: str
    notes: Optional[str]
    applied_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
