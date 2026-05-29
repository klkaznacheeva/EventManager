from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.enum import RoleList
from app.core.helper import get_role_id_by_name
from app.models.event import Event
from app.models.session import Session as EventSession
from app.models.event_participant import EventParticipant
from app.models.role import Role
from app.models.user import User
from app.services.chat_service import ChatService


class EventCoordinatorService:

    @staticmethod
    def _check_event_owner(db: Session, event_id: UUID, user_id: UUID):
        event = db.query(Event).filter(Event.id == event_id).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if event.organizer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только организатор мероприятия может управлять координаторами"
            )

        return event

    @staticmethod
    def list_coordinators(db: Session, event_id: UUID, current_user_id: UUID):
        EventCoordinatorService._check_event_owner(db, event_id, current_user_id)

        return (
            db.query(EventParticipant, User)
            .join(Role, EventParticipant.role_id == Role.id)
            .join(User, EventParticipant.user_id == User.id)
            .filter(
                EventParticipant.event_id == event_id,
                Role.name == RoleList.coordinator.value
            )
            .all()
        )

    @staticmethod
    def add_coordinator(
        db: Session,
        event_id: UUID,
        user_id: UUID,
        current_user_id: UUID
    ):
        EventCoordinatorService._check_event_owner(db, event_id, current_user_id)

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        coordinator_role_id = get_role_id_by_name(db, RoleList.coordinator)

        participant = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == user_id
            )
            .first()
        )

        if participant:
            participant.role_id = coordinator_role_id
        else:
            participant = EventParticipant(
                event_id=event_id,
                user_id=user_id,
                role_id=coordinator_role_id
            )
            db.add(participant)

        db.commit()
        db.refresh(participant)

        sessions = db.query(EventSession).filter(EventSession.event_id == event_id).all()
        for session in sessions:
            ChatService.add_coordinator_to_session(db, session.id, user_id)

        return participant

    @staticmethod
    def remove_coordinator(
        db: Session,
        event_id: UUID,
        user_id: UUID,
        current_user_id: UUID
    ):
        EventCoordinatorService._check_event_owner(db, event_id, current_user_id)

        participant = (
            db.query(EventParticipant)
            .join(Role, EventParticipant.role_id == Role.id)
            .filter(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == user_id,
                Role.name == RoleList.coordinator.value
            )
            .first()
        )

        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coordinator not found"
            )

        db.delete(participant)
        db.commit()

        return True