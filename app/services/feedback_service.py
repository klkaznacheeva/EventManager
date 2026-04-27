from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Event, EventParticipant, EventFeedback, User
from app.schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackUpdateRequest,
    FeedbackListResponse,
    FeedbackSummaryResponse,
    RatingBreakdownItem,
)


class FeedbackService:
    @staticmethod
    def _get_event(db: Session, event_id: UUID) -> Event:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Мероприятие не найдено"
            )
        return event

    @staticmethod
    def _validate_feedback_access(
        db: Session,
        event: Event,
        user: User
    ) -> None:
        if event.organizer_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Организатор не может оставлять отзыв на свое мероприятие"
            )

        is_participant = db.query(EventParticipant).filter(
            EventParticipant.event_id == event.id,
            EventParticipant.user_id == user.id
        ).first()

        if not is_participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Оставить отзыв может только участник мероприятия"
            )

        if not event.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для мероприятия не указана дата окончания"
            )

        now_utc = datetime.now(timezone.utc)

        if event.end_date > now_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Оставить отзыв можно только после завершения мероприятия"
            )

    @staticmethod
    def create_feedback(
        db: Session,
        event_id: UUID,
        data: FeedbackCreateRequest,
        current_user: User
    ) -> EventFeedback:
        event = FeedbackService._get_event(db, event_id)
        FeedbackService._validate_feedback_access(db, event, current_user)

        existing_feedback = db.query(EventFeedback).filter(
            EventFeedback.event_id == event_id,
            EventFeedback.user_id == current_user.id
        ).first()

        if existing_feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже оставили отзыв для этого мероприятия"
            )

        feedback = EventFeedback(
            event_id=event_id,
            user_id=current_user.id,
            rating=data.rating,
            comment=data.comment
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def update_feedback(
        db: Session,
        event_id: UUID,
        data: FeedbackUpdateRequest,
        current_user: User
    ) -> EventFeedback:
        event = FeedbackService._get_event(db, event_id)
        FeedbackService._validate_feedback_access(db, event, current_user)

        feedback = db.query(EventFeedback).filter(
            EventFeedback.event_id == event_id,
            EventFeedback.user_id == current_user.id
        ).first()

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ваш отзыв не найден"
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )

        for field, value in update_data.items():
            setattr(feedback, field, value)

        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_my_feedback(
        db: Session,
        event_id: UUID,
        current_user: User
    ) -> EventFeedback:
        FeedbackService._get_event(db, event_id)

        feedback = db.query(EventFeedback).filter(
            EventFeedback.event_id == event_id,
            EventFeedback.user_id == current_user.id
        ).first()

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ваш отзыв не найден"
            )

        return feedback

    @staticmethod
    def get_event_feedbacks(
        db: Session,
        event_id: UUID,
        current_user: User
    ) -> FeedbackListResponse:
        event = FeedbackService._get_event(db, event_id)

        if not current_user.is_system and event.organizer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к отзывам этого мероприятия"
            )

        feedbacks = db.query(EventFeedback).filter(
            EventFeedback.event_id == event_id
        ).order_by(EventFeedback.created_at.desc()).all()

        items = []
        for feedback in feedbacks:
            author = db.query(User).filter(User.id == feedback.user_id).first()
            feedback.author = author
            items.append(feedback)

        return FeedbackListResponse(
            items=items,
            total=len(items)
        )

    @staticmethod
    def get_event_feedback_summary(
        db: Session,
        event_id: UUID,
        current_user: User
    ) -> FeedbackSummaryResponse:
        event = FeedbackService._get_event(db, event_id)

        if not current_user.is_system and event.organizer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к статистике отзывов этого мероприятия"
            )

        total_feedbacks = db.query(func.count(EventFeedback.id)).filter(
            EventFeedback.event_id == event_id
        ).scalar() or 0

        average_rating = db.query(func.avg(EventFeedback.rating)).filter(
            EventFeedback.event_id == event_id
        ).scalar()

        grouped = db.query(
            EventFeedback.rating,
            func.count(EventFeedback.id)
        ).filter(
            EventFeedback.event_id == event_id
        ).group_by(
            EventFeedback.rating
        ).all()

        grouped_map = {rating: count for rating, count in grouped}

        breakdown = [
            RatingBreakdownItem(rating=5, count=grouped_map.get(5, 0)),
            RatingBreakdownItem(rating=4, count=grouped_map.get(4, 0)),
            RatingBreakdownItem(rating=3, count=grouped_map.get(3, 0)),
            RatingBreakdownItem(rating=2, count=grouped_map.get(2, 0)),
            RatingBreakdownItem(rating=1, count=grouped_map.get(1, 0)),
        ]

        return FeedbackSummaryResponse(
            event_id=event_id,
            total_feedbacks=total_feedbacks,
            average_rating=round(float(average_rating), 2) if average_rating is not None else 0.0,
            breakdown=breakdown
        )