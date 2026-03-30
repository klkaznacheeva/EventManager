# app/services/entity_message_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.entity_message import EntityMessage

class EntityMessageService:

    @staticmethod
    def create_message(
        db: Session,
        entity_type: str,
        entity_id: UUID,
        type: str,
        message: str,
        author_id: Optional[UUID] = None
    ) -> EntityMessage:
        db_msg = EntityMessage(
            entity_type=entity_type,
            entity_id=entity_id,
            type=type,
            message=message,
            author_id=author_id
        )
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
        return db_msg

    @staticmethod
    def get_messages(
        db: Session,
        entity_type: str,
        entity_id: UUID,
        type: Optional[str] = None
    ) -> List[EntityMessage]:
        query = db.query(EntityMessage).filter(
            EntityMessage.entity_type == entity_type,
            EntityMessage.entity_id == entity_id
        )
        if type:
            query = query.filter(EntityMessage.type == type)
        return query.order_by(EntityMessage.created_at.asc()).all()

    @staticmethod
    def get_last_message(
        db: Session,
        entity_type: str,
        entity_id: UUID,
        type: Optional[str] = None
    ) -> Optional[EntityMessage]:
        messages = EntityMessageService.get_messages(db, entity_type, entity_id, type)
        return messages[-1] if messages else None