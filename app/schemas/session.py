from pydantic import BaseModel, Field, EmailStr
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

class SessionSpeakerCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    second_name: Optional[str] = Field(default=None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=50)


class AssignSpeakerResponse(BaseModel):
    detail: str
    temporary_password: Optional[str] = None
    is_new_user: bool
    user_id: str

class SessionSpeakerResponse(BaseModel):
    id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True


class SessionSpeakerItem(BaseModel):
    id: str

    first_name: str
    second_name: Optional[str]
    last_name: str

    email: str
    phone: Optional[str]

    is_temporary: bool


class SessionSpeakerListResponse(BaseModel):
    items: List[SessionSpeakerItem]
    total: int