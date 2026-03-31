from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationOut
from app.schemas.readiness import ReadinessReport
from app.services.application_service import (
    create_application,
    get_applications,
    get_application_by_id,
    update_application,
    delete_application,
)
from app.services.job_service import get_job_by_id
from app.services.cv_version_service import get_version_by_id
from app.services.readiness_service import build_readiness_report

router = APIRouter()


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application_endpoint(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_job_by_id(db, payload.job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if payload.cv_version_id:
        version = get_version_by_id(db, payload.cv_version_id)
        if not version:
            raise HTTPException(status_code=404, detail="CV version not found.")

    return create_application(
        db=db,
        user_id=current_user.id,
        job_id=payload.job_id,
        cv_version_id=payload.cv_version_id,
        status=payload.status,
        notes=payload.notes,
    )


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_applications(db, current_user.id, status=status)


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = get_application_by_id(db, application_id, current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    return app


@router.put("/{application_id}", response_model=ApplicationOut)
def update_application_endpoint(
    application_id: uuid.UUID,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = get_application_by_id(db, application_id, current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    return update_application(
        db=db,
        application=app,
        status=payload.status,
        notes=payload.notes,
        applied_at=payload.applied_at,
    )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_endpoint(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = get_application_by_id(db, application_id, current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    delete_application(db, app)


@router.get("/{application_id}/readiness", response_model=ReadinessReport)
def get_readiness(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = get_application_by_id(db, application_id, current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    report = build_readiness_report(db, app, current_user.id)
    return ReadinessReport(**report)


@router.post("/{application_id}/apply", response_model=ApplicationOut)
def confirm_apply(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = get_application_by_id(db, application_id, current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    if app.status not in ("draft",):
        raise HTTPException(
            status_code=400,
            detail=f"Application is already in '{app.status}' status and cannot be re-applied.",
        )
    return update_application(
        db=db,
        application=app,
        status="applied",
        notes=app.notes,
        applied_at=datetime.utcnow(),
    )
