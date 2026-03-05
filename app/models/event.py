import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(255), nullable=False)
    description = Column(Text)

    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    location = Column(String(255))

    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    status = Column(String(50), default="draft")