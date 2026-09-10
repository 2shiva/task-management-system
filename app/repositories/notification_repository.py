from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, notification_id: int):
        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

    def get_by_user(self, user_id: int):
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    def create(self, notification: Notification):
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_as_read(self, notification: Notification):
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification