from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, comment_id: int):
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def get_by_task(self, task_id: int):
        return (
            self.db.query(Comment)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc())
            .all()
        )

    def create(self, comment: Comment):
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment):
        self.db.delete(comment)
        self.db.commit()