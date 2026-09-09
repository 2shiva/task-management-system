from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreateRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=5000,
    )


class CommentUpdateRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=5000,
    )


class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }