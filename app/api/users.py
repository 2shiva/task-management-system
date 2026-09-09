from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.dependencies.rbac import require_admin
from app.models import User
from app.schemas.user import (
    UserCreateRequest,
    UserListResponse,
    UserUpdateRequest,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/",
    response_model=list[UserListResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    users = db.scalars(
        select(User).order_by(User.id)
    ).all()

    return users


@router.get(
    "/{user_id}",
    response_model=UserListResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post(
    "/",
    response_model=UserListResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if user_data.role not in {"user", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'user' or 'admin'",
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.put(
    "/{user_id}",
    response_model=UserListResponse,
)
def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_data.role is not None:
        if user_data.role not in {"user", "admin"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be either 'user' or 'admin'",
            )

        user.role = user_data.role

    if user_data.email is not None:
        existing_user = db.scalar(
            select(User).where(
                User.email == user_data.email,
                User.id != user.id,
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user.email = user_data.email

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }