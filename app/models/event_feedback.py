import uuid

from sqlalchemy import Column, ForeignKey, Integer, Text, TIMESTAMP, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base


class EventFeedback(Base):
    __tablename__ = "event_feedback"

    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_feedback_event_user"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_event_feedback_rating_range"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        onupdate=func.now(),
        nullable=True
    )