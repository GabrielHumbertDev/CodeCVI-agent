import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services.cv_version_service import get_version_by_id
from app.services.cv_service import get_cv_by_id
from app.services.export_service import export_to_docx, export_to_pdf

router = APIRouter()

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_MIME = "application/pdf"


def _get_version_for_user(db: Session, version_id: uuid.UUID, user_id: uuid.UUID):
    version = get_version_by_id(db, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="CV version not found.")
    # Verify ownership via parent CV
    cv = get_cv_by_id(db, version.cv_id, user_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV version not found.")
    return version


@router.get("/versions/{version_id}/docx")
def download_docx(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    version = _get_version_for_user(db, version_id, current_user.id)
    content = export_to_docx(version.tailored_data)
    filename = f"cv_v{version.version_number}.docx"
    return Response(
        content=content,
        media_type=DOCX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/versions/{version_id}/pdf")
def download_pdf(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    version = _get_version_for_user(db, version_id, current_user.id)
    content = export_to_pdf(version.tailored_data)
    filename = f"cv_v{version.version_number}.pdf"
    return Response(
        content=content,
        media_type=PDF_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
