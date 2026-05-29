import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, UUID as SQLUUID, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base


class EventChatRoom(Base):
    __tablename__ = "event_chat_rooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)  # 'coordinators', 'speakers'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EventChatParticipant(Base):
    __tablename__ = "event_chat_participants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("event_chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint('chat_id', 'user_id'),)

class EventChatMessage(Base):
    __tablename__ = "event_chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("event_chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())