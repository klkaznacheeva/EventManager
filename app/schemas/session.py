from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.core.enum import SessionStatus


class SessionCreateRequest(BaseModel):
    event_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: Optional[str] = None
    type: Optional[str] = None
    age_limit: Optional[int] = None
    status: SessionStatus = SessionStatus.DRAFT


class SessionResponse(BaseModel):
    id: UUID
    event_id: UUID
    title: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    location: Optional[str]
    type: Optional[str]
    age_limit: Optional[int]
    status: SessionStatus
    status_label: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    items: List[SessionResponse]
    total: int

class SessionUpdateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: Optional[str] = None