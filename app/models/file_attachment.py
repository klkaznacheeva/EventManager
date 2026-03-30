# app/models/file_attachment.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class FileAttachment(Base):
    __tablename__ = "file_attachments"

    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), primary_key=True)

    entity_type = Column(String(100), primary_key=True)
    entity_id = Column(UUID(as_uuid=True), primary_key=True)

    attachment_type = Column(String(100))