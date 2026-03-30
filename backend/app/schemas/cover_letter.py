from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class CoverLetterRequest(BaseModel):
    cv_id: uuid.UUID
    job_id: uuid.UUID


class CoverLetterUpdate(BaseModel):
    content: str


class CoverLetterOut(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    version_number: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
