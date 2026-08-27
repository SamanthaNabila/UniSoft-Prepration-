from datetime import datetime

from pydantic import BaseModel, field_validator


class CommentCreate(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not (1 <= len(value) <= 2000):
            raise ValueError("Content must be between 1 and 2000 characters")
        return value


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
