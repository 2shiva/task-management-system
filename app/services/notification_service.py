from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Notification


def create_notification(
    user_id: int,
    message: str,
    task_id: int | None = None,
) -> None:
    db: Session = SessionLocal()

    try:
        notification = Notification(
            user_id=user_id,
            message=message,
            task_id=task_id,
            is_read=False,
        )

        db.add(notification)
        db.commit()

    finally:
        db.close()