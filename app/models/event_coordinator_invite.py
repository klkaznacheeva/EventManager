import uuid
import datetime

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class EventCoordinatorInvite(Base):
    __tablename__ = "event_coordinator_invites"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.id"),
        nullable=False
    )

    token = Column(
        String(255),
        unique=True,
        nullable=False
    )

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow
    )