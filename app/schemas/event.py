# app/schemas/event.py
from typing import Optional, List

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from enum import Enum

from app.core.enum import EventStatus, EventStatusMap


# Request schemas
class EventCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category_id: UUID
    start_date: datetime
    end_date: datetime
    location: Optional[str] = Field(None, max_length=255)
    status: EventStatus = EventStatus.DRAFT


class EventUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    status: Optional[EventStatus] = None


# Response schemas
class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class OrganizerResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str]
    email: str

    class Config:
        from_attributes = True


class SessionFileResponse(BaseModel):
    file_name: str
    url: str

class SessionResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    location: Optional[str]
    type: Optional[str]
    status: Optional[str]
    status_label: Optional[str] = None
    files: Optional[List[SessionFileResponse]] = None

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    category: Optional[CategoryResponse]
    start_date: datetime
    end_date: datetime
    location: Optional[str]
    organizer: Optional[OrganizerResponse]
    status: EventStatus
    status_label: Optional[str] = None
    participants_count: int = 0
    is_participant: bool = False
    created_at: datetime
    updated_at: Optional[datetime]
    sessions: Optional[List[SessionResponse]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    banner_url : Optional[str] = None

    class Config:
        from_attributes = True


class EventListRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    category_id: Optional[UUID] = None
    status: Optional[EventStatus] = None
    search: Optional[str] = None
    start_from: Optional[datetime] = None
    start_to: Optional[datetime] = None


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    page: int
    limit: int

class NeedsEditRequest(BaseModel):
    reason: str