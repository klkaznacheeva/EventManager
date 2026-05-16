import uuid

from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from app.models.base import Base


class ChecklistTaskAssignee(Base):
    __tablename__ = "checklist_task_assignees"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("checklist_tasks.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    is_completed = Column(
        Boolean,
        default=False
    )

    completed_at = Column(
        DateTime(timezone=True)
    )

    comment = Column(
        Text
    )

    created_at = Column(
        DateTime(timezone=True)
    )

    task = relationship(
        "ChecklistTask",
        back_populates="assignees"
    )

    user = relationship(
        "User"
    )

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "user_id",
            name="uq_task_user"
        ),
    )