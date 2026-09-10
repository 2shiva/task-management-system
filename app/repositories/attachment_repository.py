from sqlalchemy.orm import Session

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, attachment_id: int):
        return (
            self.db.query(Attachment)
            .filter(Attachment.id == attachment_id)
            .first()
        )

    def get_by_task(self, task_id: int):
        return (
            self.db.query(Attachment)
            .filter(Attachment.task_id == task_id)
            .order_by(Attachment.created_at.desc())
            .all()
        )

    def create(self, attachment: Attachment):
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def delete(self, attachment: Attachment):
        self.db.delete(attachment)
        self.db.commit()