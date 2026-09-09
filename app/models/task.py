from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TaskStatus(str, Enum):
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority, name="task_priority"),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status"),
        default=TaskStatus.TODO,
        nullable=False,
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        backref="assigned_tasks",
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        backref="created_tasks",
    )