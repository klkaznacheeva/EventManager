# app/services/event_service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status

from app.models.event import Event
from app.models.category import Category
from app.models.user import User
from app.models.event_participant import EventParticipant
from app.schemas.event import (
    EventCreateRequest,
    EventUpdateRequest,
    EventListRequest,
    EventResponse,
    EventListResponse
)
from app.repositories.event_repository import EventRepository


class EventService:

    @staticmethod
    def create_event(
            db: Session,
            data: EventCreateRequest,
            user_id: UUID
    ) -> Event:
        """Создание мероприятия"""
        # Проверяем существование категории
        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

        # Проверяем даты
        if data.start_date >= data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )

        # Создаем мероприятие
        event_data = data.model_dump()
        event = Event(**event_data, organizer_id=user_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        return event

    @staticmethod
    def get_event_by_id(
            db: Session,
            event_id: UUID,
            user_id: Optional[UUID] = None
    ) -> Event:
        """Получение мероприятия по ID с дополнительной информацией"""
        query = db.query(Event).options(
            joinedload(Event.category),
            joinedload(Event.organizer),
            joinedload(Event.sessions)
        ).filter(Event.id == event_id)

        event = query.first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Получаем количество участников
        participants_count = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id
        ).count()
        event.participants_count = participants_count

        # Проверяем, участвует ли пользователь
        if user_id:
            is_participant = db.query(EventParticipant).filter(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == user_id
            ).first() is not None
            event.is_participant = is_participant

        return event

    @staticmethod
    def update_event(
            db: Session,
            event_id: UUID,
            data: EventUpdateRequest,
            user_id: UUID
    ) -> Event:
        """Обновление мероприятия"""
        event = db.query(Event).filter(Event.id == event_id).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Проверяем права (только организатор может редактировать)
        if event.organizer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this event"
            )

        # Проверяем категорию если она меняется
        if data.category_id:
            category = db.query(Category).filter(Category.id == data.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )

        # Проверяем даты если они меняются
        start_date = data.start_date if data.start_date else event.start_date
        end_date = data.end_date if data.end_date else event.end_date

        if start_date >= end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )

        # Обновляем поля
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)

        db.commit()
        db.refresh(event)

        return event

    @staticmethod
    def delete_event(
            db: Session,
            event_id: UUID,
            user_id: UUID
    ) -> None:
        """Удаление мероприятия"""
        event = db.query(Event).filter(Event.id == event_id).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Проверяем права (только организатор может удалить)
        if event.organizer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this event"
            )

        db.delete(event)
        db.commit()

    @staticmethod
    def get_events_list(
            db: Session,
            data: EventListRequest,
            user_id: Optional[UUID] = None
    ) -> EventListResponse:
        """Получение списка мероприятий с фильтрацией"""
        query = db.query(Event).options(
            joinedload(Event.category),
            joinedload(Event.organizer)
        )

        # Фильтры
        if data.category_id:
            query = query.filter(Event.category_id == data.category_id)

        if data.status:
            query = query.filter(Event.status == data.status)

        if data.search:
            search_term = f"%{data.search}%"
            query = query.filter(
                or_(
                    Event.title.ilike(search_term),
                    Event.description.ilike(search_term),
                    Event.location.ilike(search_term)
                )
            )

        if data.start_from:
            query = query.filter(Event.start_date >= data.start_from)

        if data.start_to:
            query = query.filter(Event.start_date <= data.start_to)

        # Сортировка по дате начала (ближайшие первыми)
        query = query.order_by(Event.start_date.asc())

        # Подсчет общего количества
        total = query.count()

        # Пагинация
        events = query.offset((data.page - 1) * data.limit).limit(data.limit).all()

        # Добавляем дополнительную информацию для каждого события
        result_items = []
        for event in events:
            # Получаем количество участников
            participants_count = db.query(EventParticipant).filter(
                EventParticipant.event_id == event.id
            ).count()
            event.participants_count = participants_count

            # Проверяем, участвует ли пользователь
            if user_id:
                is_participant = db.query(EventParticipant).filter(
                    EventParticipant.event_id == event.id,
                    EventParticipant.user_id == user_id
                ).first() is not None
                event.is_participant = is_participant

            result_items.append(event)

        return EventListResponse(
            items=result_items,
            total=total,
            page=data.page,
            limit=data.limit
        )