from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator

Status = Literal["open", "in_progress", "resolved", "closed"]
Priority = Literal["low", "medium", "high"]


class _TicketTextFields(BaseModel):
    title: str
    description: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not (5 <= len(value) <= 200):
            raise ValueError("Title must be between 5 and 200 characters")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise ValueError("Description must be at least 10 characters")
        return value


class TicketCreate(_TicketTextFields):
    priority: Priority = "medium"


class TicketUpdate(_TicketTextFields):
    pass


class TicketStatusUpdate(BaseModel):
    status: Optional[Status] = None
    priority: Optional[Priority] = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "TicketStatusUpdate":
        if self.status is None and self.priority is None:
            raise ValueError("At least one of status or priority must be provided")
        return self


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: Status
    priority: Priority
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketStatsResponse(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int
