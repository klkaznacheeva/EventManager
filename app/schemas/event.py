from typing import Optional, List

from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from uuid import UUID


class EventListRequest(BaseModel):
    page: Optional[int] = 1
    limit: Optional[int] = 20

class SessionResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]

    sessions: Optional[List[SessionResponse]] = None

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
