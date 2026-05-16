from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Role, Event, EventParticipant
from app.schemas.user import RoleEventItem


class UserService:

    @staticmethod
    def get_roles_map(db: Session):
        roles = db.query(Role).all()
        return {r.name: r.id for r in roles}

    @staticmethod
    def build_user_roles(db: Session, user_id: UUID):

        roles_map = UserService.get_roles_map(db)

        organizer_role_id = roles_map.get("organizer")
        coordinator_role_id = roles_map.get("coordinator")
        speaker_role_id = roles_map.get("speaker")

        result = {
            "organizer": set(),
            "coordinator": set(),
            "speaker": set()
        }

        # -------------------------------------------------
        # 1. НЕЗАВЕРШЁННЫЕ СОБЫТИЯ
        # -------------------------------------------------

        events = (
            db.query(Event)
            .filter(Event.status != "completed")
            .all()
        )

        event_map = {e.id: e for e in events}

        # -------------------------------------------------
        # 2. ДЕФОЛТНЫЙ ОРГАНИЗАТОР
        # -------------------------------------------------

        for event in events:
            if event.organizer_id == user_id:
                result["organizer"].add(str(event.id))

        # -------------------------------------------------
        # 3. PARTICIPANTS
        # -------------------------------------------------

        participations = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.user_id == user_id,
                EventParticipant.role_id.in_([
                    organizer_role_id,
                    coordinator_role_id,
                    speaker_role_id
                ])
            )
            .all()
        )

        for p in participations:

            event = event_map.get(p.event_id)
            if not event:
                continue

            role_name = next(
                (name for name, rid in roles_map.items() if rid == p.role_id),
                None
            )

            if role_name in result:
                result[role_name].add(str(event.id))

        # -------------------------------------------------
        # 4. SET → LIST
        # -------------------------------------------------
        return {
            role: [
                RoleEventItem(event_id=eid)
                for eid in event_ids
            ]
            for role, event_ids in result.items()
        }