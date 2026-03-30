import os
import uuid
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


def get_upload_dir() -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR


async def save_upload_file(file: UploadFile, user_id: str) -> tuple[str, str, str]:
    """
    Validates and saves an uploaded file.
    Returns (file_path, filename, file_type)
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Only PDF and DOCX are allowed.",
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.",
        )

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    ext = ALLOWED_TYPES[file.content_type]
    unique_name = f"{user_id}_{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(get_upload_dir(), unique_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path, file.filename or unique_name, ext


def delete_file(file_path: str) -> None:
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
