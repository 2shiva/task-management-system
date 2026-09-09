from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import AuditLog, User

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can access audit logs",
        )

    logs = db.scalars(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
    ).all()

    return logs


@router.get("/{audit_log_id}")
def get_audit_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can access audit logs",
        )

    audit_log = db.get(AuditLog, audit_log_id)

    if not audit_log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found",
        )

    return audit_log