from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: str = "user"


class UserUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    email: EmailStr | None = None
    role: str | None = None
    is_active: bool | None = None


class UserListResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }