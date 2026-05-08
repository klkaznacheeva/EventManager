import uuid

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import datetime
from app.models.base import Base


class EntityMessage(Base):
    __tablename__ = "entity_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    author = relationship("User")
