import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
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

    responsible_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    age_limit = Column(Integer)

    status = Column(String(50), default="draft")