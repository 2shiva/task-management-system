from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.tasks import router as tasks_router
from app.api.comments import router as comments_router
from app.api.attachments import router as attachments_router
from app.api.notifications import router as notifications_router
from app.api.dashboard import router as dashboard_router
from app.api.audit_logs import router as audit_logs_router

app = FastAPI(
    title="Task Management System API",
    description="Backend API for Task Management System",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(comments_router)
app.include_router(attachments_router)
app.include_router(notifications_router)
app.include_router(dashboard_router)
app.include_router(audit_logs_router)


@app.get("/")
def root():
    return {"message": "Task Management System API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}