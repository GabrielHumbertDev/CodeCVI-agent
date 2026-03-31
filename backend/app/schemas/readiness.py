from pydantic import BaseModel
from typing import Optional
import uuid


class ChecklistItem(BaseModel):
    item: str
    done: bool
    action: Optional[str] = None   # guidance if not done


class ReadinessReport(BaseModel):
    application_id: uuid.UUID
    job_id: uuid.UUID
    job_title: str
    job_company: Optional[str]
    current_status: str
    overall_ready: bool

    # Match
    match_score: Optional[int]
    match_grade: Optional[str]

    # Assets
    has_tailored_cv: bool
    tailored_cv_version_id: Optional[uuid.UUID]
    has_cover_letter: bool
    cover_letter_id: Optional[uuid.UUID]

    # Checklist
    checklist: list[ChecklistItem]
