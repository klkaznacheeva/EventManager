# app/services/session_service.py
from sqlalchemy.orm import Session

from uuid import UUID
from fastapi import HTTPException, status

from app.models.file import File
from app.models.file_attachment import FileAttachment
from app.models.session import Session as SessionModel
from app.models.event_participant import EventParticipant
from app.models.role import Role
from app.core.enum import RoleList, SessionStatusMap, EntityType, AttachmentType
from app.schemas.session import SessionUpdateRequest


class SessionService:

    @staticmethod
    def create_session(db: Session, data, user_id: UUID):
        # Проверка: пользователь — организатор события
        organizer_role_id = db.query(Role.id).filter(
            Role.name == RoleList.organizer.value
        ).scalar()

        is_organizer = db.query(EventParticipant).filter(
            EventParticipant.event_id == data.event_id,
            EventParticipant.user_id == user_id,
            EventParticipant.role_id == organizer_role_id
        ).first()

        if not is_organizer:
            raise HTTPException(status_code=403, detail="Not allowed")

        session = SessionModel(
            event_id=data.event_id,
            title=data.title,
            description=data.description,
            start_date=data.start_date,
            end_date=data.end_date,
            location=data.location,
            type=data.type,
            age_limit=data.age_limit,
            status=data.status.value
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def get_session(db: Session, session_id: UUID):
        session = db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session.status_label = SessionStatusMap.SESSION_STATUS_LABELS.get(session.status, session.status)

        return session

    @staticmethod
    def get_sessions_by_event(db: Session, event_id: UUID):
        query = db.query(SessionModel).filter(
            SessionModel.event_id == event_id
        ).order_by(SessionModel.start_date.asc())

        items = query.all()

        return {
            "items": items,
            "total": len(items)
        }

    @staticmethod
    def update_session(db: Session, session_id: UUID, data: SessionUpdateRequest, user_id: UUID):
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Сессия не найдена")

        # Получаем ID организатора через EventParticipant и роль организатора
        organizer_role_id = db.query(Role.id).filter(
            Role.name == RoleList.organizer.value
        ).scalar()

        is_organizer = db.query(EventParticipant).filter(
            EventParticipant.event_id == session.event_id,  # <-- используем event_id сессии
            EventParticipant.user_id == user_id,
            EventParticipant.role_id == organizer_role_id
        ).first()

        if not is_organizer:
            raise HTTPException(status_code=403, detail="Нет прав для редактирования")

        # Обновляем поля сессии
        session.title = data.title
        session.description = data.description
        session.start_date = data.start_date
        session.end_date = data.end_date
        session.location = data.location

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: UUID, user_id: UUID):
        """
        Удаление сессии (только организатор события)
        """
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Сессия не найдена")

        # Проверка прав — только организатор события
        organizer_role_id = db.query(Role.id).filter(Role.name == RoleList.organizer.value).scalar()
        is_organizer = db.query(EventParticipant).filter(
            EventParticipant.event_id == session.event_id,
            EventParticipant.user_id == user_id,
            EventParticipant.role_id == organizer_role_id
        ).first()

        if not is_organizer:
            raise HTTPException(status_code=403, detail="Нет прав на удаление")

        db.delete(session)
        db.commit()
        return {"detail": "Сессия удалена"}
