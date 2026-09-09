from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    id: int
    task_id: int
    uploaded_by: int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)