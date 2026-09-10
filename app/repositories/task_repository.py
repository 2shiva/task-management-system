from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: int):
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_all(self):
        return self.db.query(Task).all()

    def create(self, task: Task):
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task):
        self.db.delete(task)
        self.db.commit()