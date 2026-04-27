from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.jwt_dependency import get_required_user
from app.db.database import get_db
from app.models import User
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackUpdateRequest,
    FeedbackResponse,
    FeedbackListResponse,
    FeedbackSummaryResponse,
)
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/v1/events", tags=["Feedback"])


@router.post("/{event_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    event_id: UUID,
    data: FeedbackCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    feedback = FeedbackService.create_feedback(db, event_id, data, current_user)

    author = db.query(User).filter(User.id == feedback.user_id).first()
    feedback.author = author

    return feedback


@router.put("/{event_id}/feedback", response_model=FeedbackResponse)
def update_feedback(
    event_id: UUID,
    data: FeedbackUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    feedback = FeedbackService.update_feedback(db, event_id, data, current_user)

    author = db.query(User).filter(User.id == feedback.user_id).first()
    feedback.author = author

    return feedback


@router.get("/{event_id}/feedback/my", response_model=FeedbackResponse)
def get_my_feedback(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    feedback = FeedbackService.get_my_feedback(db, event_id, current_user)

    author = db.query(User).filter(User.id == feedback.user_id).first()
    feedback.author = author

    return feedback


@router.get("/{event_id}/feedback", response_model=FeedbackListResponse)
def get_event_feedbacks(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    return FeedbackService.get_event_feedbacks(db, event_id, current_user)


@router.get("/{event_id}/feedback/summary", response_model=FeedbackSummaryResponse)
def get_event_feedback_summary(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    return FeedbackService.get_event_feedback_summary(db, event_id, current_user)