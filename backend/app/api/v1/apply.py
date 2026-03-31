import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services.cv_service import get_cv_by_id
from app.services.playwright_service import analyse_application_page

router = APIRouter()


class AssistedApplyRequest(BaseModel):
    cv_id: uuid.UUID
    url: str            # job application page URL


class FieldSuggestion(BaseModel):
    field_id: str
    field_name: str
    field_type: str
    label: str
    suggested_value: Optional[str]
    has_suggestion: bool


class AssistedApplyResponse(BaseModel):
    url: str
    page_title: str
    status: str
    total_fields: int
    suggested_fields: int
    fields: list[FieldSuggestion]
    screenshot_base64: Optional[str]
    error: Optional[str]


@router.post("", response_model=AssistedApplyResponse)
async def assisted_apply(
    payload: AssistedApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Visit a job application URL with a headless browser, detect form fields,
    and suggest CV data for each field. Does NOT submit anything.
    """
    cv = get_cv_by_id(db, payload.cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    if cv.parse_status != "done" or not cv.parsed_data:
        raise HTTPException(status_code=400, detail="CV must be parsed before assisted apply.")

    result = await analyse_application_page(payload.url, cv.parsed_data)

    return AssistedApplyResponse(**result)
