from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserRegister, UserLogin, UserOut, TokenOut
from app.services.user_service import get_user_by_email, create_user, set_last_login
from app.api.v1.deps import get_current_user
from app.models.user import User, UserStatus

router = APIRouter()

# Human-readable messages for each blocked status
_STATUS_MESSAGES = {
    UserStatus.PENDING:  "Your account is pending admin approval. Please wait for confirmation.",
    UserStatus.PAUSED:   "Your account has been paused. Please contact support.",
    UserStatus.DISABLED: "Your account has been disabled. Please contact support.",
}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # New users always start as pending_approval
    user = create_user(db, email=payload.email, password=payload.password, full_name=payload.full_name)
    return user


@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)

    # Wrong credentials — generic message to avoid user enumeration
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Block non-active accounts with specific messages
    if user.status != UserStatus.ACTIVE:
        msg = _STATUS_MESSAGES.get(user.status, "Account access restricted.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)

    # Record login time
    set_last_login(db, user)

    token = create_access_token(subject=str(user.id))
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
