import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from app.models.base import Base


class ChecklistTask(Base):
    __tablename__ = "checklist_tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    entity_type = Column(
        String(50),
        nullable=False
    )

    entity_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text
    )

    deadline = Column(
        DateTime(timezone=True)
    )

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id")
    )

    created_at = Column(
        DateTime(timezone=True)
    )

    updated_at = Column(
        DateTime(timezone=True)
    )

    creator = relationship(
        "User"
    )

    assignees = relationship(
        "ChecklistTaskAssignee",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin"
    )