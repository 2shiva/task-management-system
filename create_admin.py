from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User


ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin12345"


def create_admin():
    db = SessionLocal()

    try:
        existing_admin = db.scalar(
            select(User).where(User.email == ADMIN_EMAIL)
        )

        if existing_admin:
            print("Admin user already exists.")
            return

        admin = User(
            name="System Admin",
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin user created successfully.")
        print(f"Email: {ADMIN_EMAIL}")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()