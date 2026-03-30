from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import uuid


class CVVersionOut(BaseModel):
    id: uuid.UUID
    cv_id: uuid.UUID
    job_id: Optional[uuid.UUID]
    version_number: int
    tailored_data: Any
    validation_passed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TailorRequest(BaseModel):
    cv_id: uuid.UUID
    job_id: uuid.UUID
