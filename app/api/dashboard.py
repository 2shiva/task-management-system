from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Task, TaskStatus, User

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail="Only admins can access the admin dashboard",
        )

    total_users = db.scalar(
        select(func.count(User.id))
    )

    active_users = db.scalar(
        select(func.count(User.id)).where(User.is_active.is_(True))
    )

    inactive_users = db.scalar(
        select(func.count(User.id)).where(User.is_active.is_(False))
    )

    total_tasks = db.scalar(
        select(func.count(Task.id))
    )

    todo_tasks = db.scalar(
        select(func.count(Task.id)).where(Task.status == TaskStatus.TODO)
    )

    in_progress_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.status == TaskStatus.IN_PROGRESS
        )
    )

    completed_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.status == TaskStatus.COMPLETED
        )
    )

    cancelled_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.status == TaskStatus.CANCELLED
        )
    )

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": inactive_users,
        },
        "tasks": {
            "total": total_tasks,
            "todo": todo_tasks,
            "in_progress": in_progress_tasks,
            "completed": completed_tasks,
            "cancelled": cancelled_tasks,
        },
    }


@router.get("/user")
def user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    created_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.created_by == current_user.id
        )
    )

    assigned_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.assigned_to == current_user.id
        )
    )

    completed_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.assigned_to == current_user.id,
            Task.status == TaskStatus.COMPLETED,
        )
    )

    pending_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.assigned_to == current_user.id,
            Task.status != TaskStatus.COMPLETED,
        )
    )

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        },
        "tasks": {
            "created": created_tasks,
            "assigned": assigned_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks,
        },
    }