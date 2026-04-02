from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Admin schemas
# ---------------------------------------------------------------------------

class AdminUserOut(BaseModel):
    """Full user detail for admin view."""
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    role: str
    status: str
    is_active: bool
    is_deleted: bool
    approved_at: Optional[datetime]
    approved_by: Optional[uuid.UUID]
    paused_at: Optional[datetime]
    pause_reason: Optional[str]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUserEdit(BaseModel):
    """Fields an admin can update directly."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None


class AdminPauseRequest(BaseModel):
    reason: Optional[str] = None
