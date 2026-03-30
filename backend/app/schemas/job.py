from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import uuid


class JobCreate(BaseModel):
    title: str
    company: Optional[str] = None
    description: str


class JobOut(BaseModel):
    id: uuid.UUID
    title: str
    company: Optional[str]
    description: str
    extracted_keywords: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class JobListOut(BaseModel):
    jobs: list[JobOut]
    total: int
