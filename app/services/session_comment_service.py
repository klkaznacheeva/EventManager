from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.entity_message import EntityMessage
from app.services.session_service import SessionService


class SessionCommentService:
    @staticmethod
    def get_comments(
        db: Session,
        session_id: UUID
    ):
        session = SessionService.get_by_id(db, session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return (
            db.query(EntityMessage)
            .options(joinedload(EntityMessage.author))
            .filter(
                EntityMessage.entity_type == "session",
                EntityMessage.entity_id == session_id,
                EntityMessage.type == "comment"
            )
            .order_by(EntityMessage.created_at.asc())
            .all()
        )

    @staticmethod
    def create_comment(
        db: Session,
        session_id: UUID,
        user_id: UUID,
        message: str
    ):
        session = SessionService.get_by_id(db, session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        text = message.strip()

        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Комментарий не может быть пустым"
            )

        comment = EntityMessage(
            entity_type="session",
            entity_id=session_id,
            type="comment",
            message=text,
            author_id=user_id
        )

        db.add(comment)
        db.commit()
        db.refresh(comment)

        return comment