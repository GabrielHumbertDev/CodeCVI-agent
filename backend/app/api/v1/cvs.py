from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.storage import save_upload_file, delete_file
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.cv import CVOut, CVListOut
from app.services.cv_service import (
    create_cv_record, get_cvs_by_user, get_cv_by_id,
    delete_cv_record, update_cv_parsed_data,
)
from app.services.cv_parser import parse_cv
import uuid

router = APIRouter()


@router.post("/upload", response_model=CVOut, status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path, filename, file_type = await save_upload_file(file, str(current_user.id))
    try:
        cv = create_cv_record(
            db=db,
            user_id=current_user.id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
        )
    except Exception:
        delete_file(file_path)
        raise HTTPException(status_code=500, detail="Failed to save CV record.")

    # Parse immediately after upload
    try:
        parsed = parse_cv(file_path, file_type)
        cv = update_cv_parsed_data(db, cv, parsed_data=parsed, status="done")
    except Exception as e:
        # Parsing failure is non-fatal — file is saved, status stays pending
        update_cv_parsed_data(db, cv, parsed_data=None, status="failed")

    return cv


@router.get("", response_model=CVListOut)
def list_cvs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cvs = get_cvs_by_user(db, current_user.id)
    return CVListOut(cvs=cvs, total=len(cvs))


@router.get("/{cv_id}", response_model=CVOut)
def get_cv(
    cv_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cv = get_cv_by_id(db, cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    return cv


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cv(
    cv_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cv = get_cv_by_id(db, cv_id, current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found.")
    delete_file(cv.file_path)
    delete_cv_record(db, cv)
