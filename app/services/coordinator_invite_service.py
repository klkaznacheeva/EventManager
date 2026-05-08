import datetime
import secrets
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enum import RoleList
from app.core.helper import get_role_id_by_name
from app.models import EventParticipant
from app.models.event import Event
from app.models.event_coordinator_invite import EventCoordinatorInvite


class CoordinatorInviteService:
    @staticmethod
    def create_invite(
        db: Session,
        event_id: UUID,
        current_user_id: UUID,
        expires_in_days: int | None = 7
    ):
        event = (
            db.query(Event)
            .filter(Event.id == event_id)
            .first()
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if event.organizer_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только организатор мероприятия может создавать ссылки координаторов"
            )

        token = secrets.token_urlsafe(32)

        expires_at = None

        if expires_in_days:
            expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                days=expires_in_days
            )

        invite = EventCoordinatorInvite(
            event_id=event_id,
            token=token,
            created_by=current_user_id,
            is_active=True,
            expires_at=expires_at
        )

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return invite

    @staticmethod
    def accept_invite(
        db: Session,
        token: str,
        user_id: UUID
    ):
        invite = (
            db.query(EventCoordinatorInvite)
            .filter(EventCoordinatorInvite.token == token)
            .first()
        )

        if not invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invite not found"
            )

        if not invite.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite is not active"
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        if invite.expires_at and invite.expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite expired"
            )

        coordinator_role_id = get_role_id_by_name(
            db,
            RoleList.coordinator
        )

        participant = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == invite.event_id,
                EventParticipant.user_id == user_id
            )
            .first()
        )

        if participant:
            participant.role_id = coordinator_role_id
        else:
            participant = EventParticipant(
                event_id=invite.event_id,
                user_id=user_id,
                role_id=coordinator_role_id
            )
            db.add(participant)

        db.commit()
        db.refresh(participant)

        return participant