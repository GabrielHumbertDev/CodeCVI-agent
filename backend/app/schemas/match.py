from pydantic import BaseModel
from typing import Optional
import uuid


class MatchRequest(BaseModel):
    cv_id: uuid.UUID
    job_id: uuid.UUID


class MatchResult(BaseModel):
    cv_id: uuid.UUID
    job_id: uuid.UUID
    score: int
    total_keywords: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    job_keywords: list[str]
