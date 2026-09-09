from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Comment, Task, TaskStatus, User
from app.schemas.comment import (
    CommentCreateRequest,
    CommentResponse,
    CommentUpdateRequest,
)

router = APIRouter(
    prefix="/tasks",
    tags=["Comments"],
)


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    task_id: int,
    comment_data: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user.role != "admin":
        if (
            task.created_by != current_user.id
            and task.assigned_to != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to comment on this task",
            )

    if task.status in {
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed or cancelled tasks cannot receive new comments",
        )

    comment = Comment(
        task_id=task.id,
        user_id=current_user.id,
        content=comment_data.content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.get(
    "/{task_id}/comments",
    response_model=list[CommentResponse],
)
def get_comments(
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

    if current_user.role != "admin":
        if (
            task.created_by != current_user.id
            and task.assigned_to != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this task",
            )

    comments = db.scalars(
        select(Comment)
        .where(Comment.task_id == task_id)
        .order_by(Comment.created_at)
    ).all()

    return comments


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.get(Comment, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own comments",
        )

    task = db.get(Task, comment.task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.status in {
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments on completed or cancelled tasks cannot be modified",
        )

    comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.get(Comment, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}