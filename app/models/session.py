import datetime
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.enum import EventStatus, SessionStatus
from app.models.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"))

    title = Column(String(255), nullable=False)
    description = Column(Text)

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    location = Column(String(255))
    type = Column(String(100))

    responsible_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    age_limit = Column(Integer)

    status = Column(Enum(SessionStatus), default=SessionStatus.draft, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow())
    updated_at = Column(DateTime(timezone=True))

    # ОБРАТНАЯ СВЯЗЬ
    event = relationship("Event", back_populates="sessions")