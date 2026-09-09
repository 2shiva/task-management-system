from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    assigned_to: int | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    due_date: date | None = None


class TaskAssignRequest(BaseModel):
    assigned_to: int


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus


class TaskPriorityUpdateRequest(BaseModel):
    priority: TaskPriority


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    assigned_to: int | None
    created_by: int
    priority: TaskPriority
    status: TaskStatus
    due_date: date | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}