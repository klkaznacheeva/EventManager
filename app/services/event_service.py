from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, func, distinct
from sqlalchemy.orm import Session, joinedload

from app.core.enum import (
    RoleList,
    EventStatusMap,
    SessionStatusMap,
    EventStatus,
    SessionStatus,
)
from app.core.helper import get_role_id_by_name
from app.models import Role, Event
from app.models.category import Category
from app.models.event_participant import EventParticipant
from app.models.session import Session as EventSession
from app.models.session_participant import SessionParticipant
from app.models.user import User
from app.schemas.event import (
    EventCreateRequest,
    EventUpdateRequest,
    EventListRequest,
    EventListResponse,
)
from app.schemas.session import SessionSpeakerResponse
from app.services.file_service import FileService


class EventService:

    @staticmethod
    def create_event(
        db: Session,
        data: EventCreateRequest,
        user_id: UUID
    ) -> Event:
        """Создание мероприятия"""

        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

        if data.start_date >= data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )

        event_data = data.model_dump()
        event = Event(**event_data, organizer_id=user_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        organizer_role_id = db.query(Role.id).filter(
            Role.name == RoleList.organizer.value
        ).scalar()

        event_participant = EventParticipant(
            event_id=event.id,
            user_id=user_id,
            role_id=organizer_role_id
        )

        db.add(event_participant)
        db.commit()

        return event

    @staticmethod
    def get_event_by_id(
            db: Session,
            event_id: UUID,
            user_id: Optional[UUID] = None
    ) -> Event:
        """Получение мероприятия по ID с дополнительной информацией"""

        query = (
            db.query(Event)
            .options(
                joinedload(Event.category),
                joinedload(Event.organizer),
                joinedload(Event.sessions)
                .joinedload(EventSession.participants)
                .joinedload(SessionParticipant.user),
                joinedload(Event.sessions)
                .joinedload(EventSession.participants)
                .joinedload(SessionParticipant.role),
            )
            .filter(Event.id == event_id)
        )

        event = query.first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        participants_count = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id
        ).count()
        event.participants_count = participants_count

        event.is_participant = False
        if user_id:
            is_participant = db.query(EventParticipant).filter(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == user_id
            ).first() is not None
            event.is_participant = is_participant

        event.status_label = EventStatusMap.EVENT_STATUS_LABELS.get(
            event.status,
            event.status
        )

        # Добавляем статусные лейблы и флаг присоединения для сессий
        for session in event.sessions:
            session.status_label = SessionStatusMap.SESSION_STATUS_LABELS.get(
                session.status,
                session.status
            )

            session_files = FileService.get_session_files(db, session.id)
            session.files = session_files

            session.speakers = [
                SessionSpeakerResponse.model_validate(p.user)
                for p in session.participants
                if p.role and p.role.name == RoleList.speaker.value
            ]

            # Вычисляем, присоединился ли текущий пользователь к этой сессии
            session.current_user_joined = False
            if user_id:
                joined = db.query(SessionParticipant).filter(
                    SessionParticipant.session_id == session.id,
                    SessionParticipant.user_id == user_id
                ).first() is not None
                session.current_user_joined = joined

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

        if event.organizer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this event"
            )

        if data.category_id:
            category = db.query(Category).filter(Category.id == data.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )

        start_date = data.start_date if data.start_date else event.start_date
        end_date = data.end_date if data.end_date else event.end_date

        if start_date >= end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )

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
            user_id: Optional[UUID] = None,
            user_mode: str = "organizer"
    ) -> EventListResponse:
        """Получение списка мероприятий с учетом режима пользователя"""
        print("GET_EVENTS_LIST")
        query = db.query(Event).options(
            joinedload(Event.category),
            joinedload(Event.organizer)
        )

        user = None

        if user_id:
            user = db.query(User).filter(User.id == user_id).first()

        # ---------------------------------------------------------
        # ROLE LOGIC
        # ---------------------------------------------------------

        if user and user.is_system:
            # Админ видит все
            pass

        elif user_mode == "organizer":
            if not user_id:
                query = query.filter(False)
            else:
                # Получаем ID мероприятий, где пользователь является координатором
                coordinator_event_ids = db.query(EventParticipant.event_id).filter(
                    EventParticipant.user_id == user_id,
                    EventParticipant.role_id == get_role_id_by_name(db, RoleList.coordinator)
                ).subquery()
                # Получаем ID мероприятий, где пользователь является соорганизатором
                organizer_event_ids = db.query(EventParticipant.event_id).filter(
                    EventParticipant.user_id == user_id,
                    EventParticipant.role_id == get_role_id_by_name(db, RoleList.organizer)
                ).subquery()
                query = query.filter(
                    or_(
                        Event.organizer_id == user_id,
                        Event.id.in_(coordinator_event_ids),
                        Event.id.in_(organizer_event_ids)
                    )
                )

        elif user_mode == "participant":
            # Участник видит опубликованные мероприятия
            query = query.filter(
                Event.status == EventStatus.PUBLISHED.value
            )

        elif user_mode == "speaker":
            # Спикер видит мероприятия,
            # где он назначен спикером в сессиях
            query = (
                query.join(Event.sessions)
                .join(EventSession.participants)
                .filter(SessionParticipant.user_id == user_id)
                .distinct()
            )

        else:
            # Безопасное поведение по умолчанию
            query = query.filter(
                Event.status == EventStatus.PUBLISHED.value
            )

        # ---------------------------------------------------------
        # FILTERS
        # ---------------------------------------------------------

        if data.category_id:
            query = query.filter(
                Event.category_id == data.category_id
            )

        if data.status:
            query = query.filter(
                Event.status == data.status
            )

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
            query = query.filter(
                Event.start_date >= data.start_from
            )

        if data.start_to:
            query = query.filter(
                Event.start_date <= data.start_to
            )

        # ---------------------------------------------------------
        # SORTING
        # ---------------------------------------------------------

        query = query.order_by(
            Event.start_date.asc()
        )

        # ---------------------------------------------------------
        # PAGINATION
        # ---------------------------------------------------------

        total = query.count()

        events = (
            query.offset((data.page - 1) * data.limit)
            .limit(data.limit)
            .all()
        )

        # ---------------------------------------------------------
        # RESPONSE BUILD
        # ---------------------------------------------------------

        result_items = []

        participant_role_id = get_role_id_by_name(
            db,
            RoleList.user
        )

        for event in events:

            participants_count = db.query(EventParticipant).filter(
                EventParticipant.event_id == event.id,
                EventParticipant.role_id == participant_role_id
            ).count()

            event.participants_count = participants_count

            # Пользователь участвует?
            event.is_participant = False

            if user_id:
                event.is_participant = (
                        db.query(EventParticipant)
                        .filter(
                            EventParticipant.event_id == event.id,
                            EventParticipant.user_id == user_id
                        )
                        .first()
                        is not None
                )

            # Статус label
            event.status_label = EventStatusMap.EVENT_STATUS_LABELS.get(
                event.status,
                event.status
            )

            result_items.append(event)

        return EventListResponse(
            items=result_items,
            total=total,
            page=data.page,
            limit=data.limit
        )

    @staticmethod
    def publish_event(
        db: Session,
        event_id: UUID,
        user_id: UUID
    ):
        event = db.query(Event).filter(Event.id == event_id).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if str(event.organizer_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed"
            )

        if event.status == EventStatus.PUBLISHED.value:
            return {"message": "Уже опубликовано"}

        event.status = EventStatus.PUBLISHED.value

        db.query(EventSession).filter(
            EventSession.event_id == event_id,
            EventSession.status == SessionStatus.DRAFT.value
        ).update(
            {EventSession.status: SessionStatus.PUBLISHED.value},
            synchronize_session=False
        )

        db.commit()

        return {"message": "Мероприятие опубликовано"}

    @staticmethod
    def complete_event(db: Session, event_id: UUID, user_id: UUID):
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if str(event.organizer_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Not allowed")

        # Можно завершить только опубликованное мероприятие (или любое, кроме уже завершённого)
        if event.status == EventStatus.COMPLETED.value:
            return {"message": "Мероприятие уже завершено"}

        if event.status != EventStatus.PUBLISHED.value:
            raise HTTPException(
                status_code=400,
                detail="Only published events can be completed"
            )

        # Обновляем статус события
        event.status = EventStatus.COMPLETED.value

        # Завершаем все сессии мероприятия (если у них есть статус)
        # Предположим, что у сессии есть статус SessionStatus (DRAFT, PUBLISHED, COMPLETED)
        db.query(EventSession).filter(
            EventSession.event_id == event_id,
            EventSession.status != SessionStatus.COMPLETED.value
        ).update(
            {EventSession.status: SessionStatus.COMPLETED.value},
            synchronize_session=False
        )

        db.commit()

        # Можно также отправить уведомления участникам / координаторам / спикерам
        # (опционально, но для пет-проекта можно пропустить)

        return {"message": "Мероприятие завершено"}

    @staticmethod
    def join_event(
        db: Session,
        event_id: UUID,
        user_id: UUID
    ):
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if event.status != EventStatus.PUBLISHED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Можно записаться только на опубликованное мероприятие"
            )

        participant = db.query(EventParticipant).filter_by(
            event_id=event_id,
            user_id=user_id
        ).first()

        if participant:
            return participant

        participant_role_id = get_role_id_by_name(
            db,
            RoleList.user
        )

        participant = EventParticipant(
            event_id=event_id,
            user_id=user_id,
            role_id=participant_role_id
        )
        db.add(participant)
        db.commit()
        db.refresh(participant)

        return participant

    @staticmethod
    def leave_event(
            db: Session,
            event_id: UUID,
            user_id: UUID
    ):
        event = db.query(Event).filter(Event.id == event_id).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        participant = db.query(EventParticipant).filter_by(
            event_id=event_id,
            user_id=user_id
        ).first()

        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вы не записаны на это мероприятие"
            )

        db.delete(participant)
        db.commit()

        return True

    @staticmethod
    def get_participants_count(
            db: Session,
            event_id: UUID
    ):
        participant_role_id = get_role_id_by_name(
            db,
            RoleList.user
        )

        return db.query(
            func.count(distinct(EventParticipant.user_id))
        ).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.role_id == participant_role_id
        ).scalar()

    @staticmethod
    def get_coordinator_events(
            db: Session,
            user_id: UUID
    ):

        events = (
            db.query(Event)
            .join(
                EventParticipant,
                EventParticipant.event_id == Event.id
            )
            .join(
                Role,
                Role.id == EventParticipant.role_id
            )
            .filter(
                EventParticipant.user_id == user_id,
                Role.name == "coordinator"
            )
            .order_by(Event.start_date.desc())
            .all()
        )

        return {
            "items": events
        }