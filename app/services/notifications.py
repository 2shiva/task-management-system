from sqlalchemy.orm import Session

from app.models import Notification


def create_notification(
    db: Session,
    user_id: int,
    message: str,
    task_id: int | None = None,
):
    notification = Notification(
        user_id=user_id,
        task_id=task_id,
        message=message,
        is_read=False,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification