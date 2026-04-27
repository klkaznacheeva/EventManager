from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackCreateRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)


class FeedbackUpdateRequest(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)


class FeedbackAuthorResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    id: UUID
    event_id: UUID
    user_id: UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: Optional[FeedbackAuthorResponse] = None

    class Config:
        from_attributes = True


class RatingBreakdownItem(BaseModel):
    rating: int
    count: int


class FeedbackSummaryResponse(BaseModel):
    event_id: UUID
    total_feedbacks: int
    average_rating: float
    breakdown: List[RatingBreakdownItem]


class FeedbackListResponse(BaseModel):
    items: List[FeedbackResponse]
    total: int