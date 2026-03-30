from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import uuid


class CVOut(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str
    parse_status: str
    parsed_data: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class CVListOut(BaseModel):
    cvs: list[CVOut]
    total: int
