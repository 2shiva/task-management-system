import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Attachment, Task, TaskStatus, User
from app.schemas.attachment import AttachmentResponse


router = APIRouter(
    prefix="/tasks",
    tags=["Attachments"],
)


UPLOAD_DIR = "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".doc",
    ".docx",
    ".txt",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/{task_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user.role != "admin" and (
        task.created_by != current_user.id
        and task.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this task",
        )

    if task.status in {TaskStatus.COMPLETED, TaskStatus.CANCELLED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed or cancelled tasks cannot receive new attachments",
        )

    extension = os.path.splitext(file.filename or "")[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: PDF, JPG, JPEG, PNG, DOC, DOCX, TXT",
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size cannot exceed 10 MB",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    stored_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    attachment = Attachment(
        task_id=task_id,
        uploaded_by=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=len(content),
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment


@router.get(
    "/{task_id}/attachments",
    response_model=list[AttachmentResponse],
)
def get_attachments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user.role != "admin" and (
        task.created_by != current_user.id
        and task.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this task",
        )

    result = db.scalars(
        select(Attachment)
        .where(Attachment.task_id == task_id)
        .order_by(Attachment.created_at.desc())
    )

    return result.all()


@router.delete(
    "/attachments/{attachment_id}",
)
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attachment = db.get(Attachment, attachment_id)

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    if (
        attachment.uploaded_by != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own attachments",
        )

    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)

    db.delete(attachment)
    db.commit()

    return {
        "message": "Attachment deleted successfully"
    }