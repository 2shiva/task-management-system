from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Task, TaskPriority, TaskStatus, User
from app.schemas.task import (
    TaskAssignRequest,
    TaskCreateRequest,
    TaskPriorityUpdateRequest,
    TaskResponse,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
)
from app.services.audit_logs import create_audit_log
from app.services.notifications import create_notification

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if task_data.assigned_to is not None:
        assigned_user = db.get(User, task_data.assigned_to)

        if not assigned_user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found",
            )

        if not assigned_user.is_active:
            raise HTTPException(
                status_code=400,
                detail="Inactive users cannot be assigned new tasks",
            )

    task = Task(
        title=task_data.title,
        description=task_data.description,
        assigned_to=task_data.assigned_to,
        created_by=current_user.id,
        priority=task_data.priority,
        status=TaskStatus.TODO,
        due_date=task_data.due_date,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Task",
        entity_id=task.id,
        description=f"Task '{task.title}' was created",
    )

    if task.assigned_to and task.assigned_to != current_user.id:
        create_notification(
            db,
            task.assigned_to,
            f"You have been assigned a new task: {task.title}",
            task.id,
        )

    return task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    search: str | None = None,
    status_filter: TaskStatus | None = None,
    priority_filter: TaskPriority | None = None,
    assigned_to: int | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than or equal to 1",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100",
        )

    query = select(Task)

    if current_user.role != "admin":
        query = query.where(
            (Task.created_by == current_user.id)
            | (Task.assigned_to == current_user.id)
        )

    if search:
        search_pattern = f"%{search}%"

        query = query.where(
            Task.title.ilike(search_pattern)
            | Task.description.ilike(search_pattern)
        )

    if status_filter:
        query = query.where(Task.status == status_filter)

    if priority_filter:
        query = query.where(Task.priority == priority_filter)

    if assigned_to is not None:
        query = query.where(Task.assigned_to == assigned_to)

    sort_columns = {
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
        "due_date": Task.due_date,
        "title": Task.title,
        "priority": Task.priority,
        "status": Task.status,
    }

    if sort_by not in sort_columns:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort field. Allowed: "
                "created_at, updated_at, due_date, title, priority, status"
            ),
        )

    if sort_order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=400,
            detail="Sort order must be 'asc' or 'desc'",
        )

    sort_column = sort_columns[sort_by]

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    return db.scalars(query).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if current_user.role != "admin" and (
        task.created_by != current_user.id
        and task.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this task",
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if current_user.role != "admin" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the task creator or admin can modify this task",
        )

    if task.status in {TaskStatus.COMPLETED, TaskStatus.CANCELLED}:
        raise HTTPException(
            status_code=400,
            detail=f"{task.status.value} tasks cannot be modified",
        )

    if task_data.title is not None:
        task.title = task_data.title

    if task_data.description is not None:
        task.description = task_data.description

    if task_data.due_date is not None:
        task.due_date = task_data.due_date

    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Task",
        entity_id=task.id,
        description=f"Task '{task.title}' was updated",
    )

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if current_user.role != "admin" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the task creator or admin can delete this task",
        )

    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Completed tasks cannot be deleted",
        )

    task_title = task.title
    task_id_value = task.id

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Task",
        entity_id=task_id_value,
        description=f"Task '{task_title}' was deleted",
    )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }


@router.put("/{task_id}/assign", response_model=TaskResponse)
def assign_task(
    task_id: int,
    assign_data: TaskAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can assign tasks",
        )

    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if task.status in {TaskStatus.COMPLETED, TaskStatus.CANCELLED}:
        raise HTTPException(
            status_code=400,
            detail="Completed or cancelled tasks cannot be reassigned",
        )

    assigned_user = db.get(User, assign_data.assigned_to)

    if not assigned_user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found",
        )

    if not assigned_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive users cannot be assigned new tasks",
        )

    old_assigned_to = task.assigned_to

    task.assigned_to = assigned_user.id

    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="ASSIGN",
        entity_type="Task",
        entity_id=task.id,
        description=(
            f"Task '{task.title}' was assigned to user "
            f"{assigned_user.id}"
        ),
    )

    create_notification(
        db,
        assigned_user.id,
        f"You have been assigned task: {task.title}",
        task.id,
    )

    return task


@router.put("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if current_user.role != "admin" and (
        task.created_by != current_user.id
        and task.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to modify this task",
        )

    valid_transitions = {
        TaskStatus.TODO: {
            TaskStatus.IN_PROGRESS,
            TaskStatus.CANCELLED,
        },
        TaskStatus.IN_PROGRESS: {
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        },
        TaskStatus.COMPLETED: set(),
        TaskStatus.CANCELLED: set(),
    }

    current_status = task.status
    new_status = status_data.status

    if new_status not in valid_transitions[current_status]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition from "
                f"'{current_status.value}' to '{new_status.value}'"
            ),
        )

    old_status = task.status

    task.status = new_status

    if new_status == TaskStatus.COMPLETED:
        task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="STATUS_CHANGE",
        entity_type="Task",
        entity_id=task.id,
        description=(
            f"Task '{task.title}' status changed from "
            f"'{old_status.value}' to '{new_status.value}'"
        ),
    )

    recipient = None

    if task.assigned_to and task.assigned_to != current_user.id:
        recipient = task.assigned_to
    elif task.created_by != current_user.id:
        recipient = task.created_by

    if recipient:
        create_notification(
            db,
            recipient,
            f"Task '{task.title}' status changed to {new_status.value}",
            task.id,
        )

    return task


@router.put("/{task_id}/priority", response_model=TaskResponse)
def update_task_priority(
    task_id: int,
    priority_data: TaskPriorityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if current_user.role != "admin" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the task creator or admin can modify task priority",
        )

    if task.status in {TaskStatus.COMPLETED, TaskStatus.CANCELLED}:
        raise HTTPException(
            status_code=400,
            detail=f"{task.status.value} tasks cannot be modified",
        )

    old_priority = task.priority

    task.priority = priority_data.priority

    db.commit()
    db.refresh(task)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="PRIORITY_CHANGE",
        entity_type="Task",
        entity_id=task.id,
        description=(
            f"Task '{task.title}' priority changed from "
            f"'{old_priority.value}' to "
            f"'{task.priority.value}'"
        ),
    )

    return task