from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, audit_log_id: int):
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.id == audit_log_id)
            .first()
        )

    def get_all(self):
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def create(self, audit_log: AuditLog):
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log