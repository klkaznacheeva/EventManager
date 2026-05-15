# app/services/session_service.py
import logging

from sqlalchemy.orm import Session

from uuid import UUID
from fastapi import HTTPException, status

from app.core.helper import generate_temporary_password
from app.core.security import hash_password
from app.models import User, event
from app.models.file import File
from app.models.file_attachment import FileAttachment
from app.models.session import Session as SessionModel
from app.models.event_participant import EventParticipant
from app.models.role import Role
from app.core.enum import RoleList, SessionStatusMap, EntityType, AttachmentType
from app.models.session_participant import SessionParticipant
from app.schemas.session import SessionUpdateRequest
from app.services.notification_service import NotificationService


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

    @staticmethod
    def get_by_id(
            db: Session,
            session_id: UUID
    ):
        return db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()

    @staticmethod
    async def assign_speaker(
            db: Session,
            session_id: UUID,
            data,
            current_user_id: UUID
    ):
        """
        Назначение спикера на сессию.
        Если пользователь не существует — создается временный аккаунт.
        """

        session = db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Сессия не найдена"
            )

        # ---------------------------------------------------
        # Проверяем права организатора
        # ---------------------------------------------------

        organizer_role_id = db.query(Role.id).filter(
            Role.name == RoleList.organizer.value
        ).scalar()

        is_owner = session.event.organizer_id == current_user_id
        is_organizer = is_owner or db.query(EventParticipant).filter(
            EventParticipant.event_id == session.event_id,
            EventParticipant.user_id == current_user_id,
            EventParticipant.role_id == organizer_role_id
        ).first()

        print("IS_ORGANIZER:{}".format(is_organizer))

        if not is_organizer:
            raise HTTPException(
                status_code=403,
                detail="Нет прав на назначение спикера"
            )

        # ---------------------------------------------------
        # Получаем роль speaker
        # ---------------------------------------------------

        speaker_role = db.query(Role).filter(
            Role.name == RoleList.speaker.value
        ).first()

        if not speaker_role:
            raise HTTPException(
                status_code=500,
                detail="Роль speaker не найдена"
            )

        # ---------------------------------------------------
        # Ищем пользователя
        # ---------------------------------------------------

        user = None

        if data.email:
            user = db.query(User).filter(
                User.email == data.email
            ).first()

        if not user and data.phone:
            user = db.query(User).filter(
                User.phone == data.phone
            ).first()

        temporary_password = None
        is_new_user = False

        # ---------------------------------------------------
        # Создаем пользователя если не найден
        # ---------------------------------------------------

        if not user:
            temporary_password = generate_temporary_password()

            user = User(
                first_name=data.first_name,
                second_name=data.second_name,
                last_name=data.last_name,
                email=data.email,
                phone=data.phone,
                password_hash=hash_password(temporary_password),
                is_temporary=True,
                password_changed=False,
                invited_by=current_user_id
            )

            db.add(user)
            db.flush()

            is_new_user = True

        # ---------------------------------------------------
        # Проверяем participation мероприятия
        # ---------------------------------------------------

        existing_event_participant = db.query(EventParticipant).filter(
            EventParticipant.event_id == session.event_id,
            EventParticipant.user_id == user.id
        ).first()

        if not existing_event_participant:
            event_participant = EventParticipant(
                event_id=session.event_id,
                user_id=user.id,
                role_id=speaker_role.id
            )

            db.add(event_participant)

        # ---------------------------------------------------
        # Проверяем participation сессии
        # ---------------------------------------------------

        existing_session_participant = db.query(SessionParticipant).filter(
            SessionParticipant.session_id == session.id,
            SessionParticipant.user_id == user.id
        ).first()

        if existing_session_participant:
            raise HTTPException(
                status_code=400,
                detail="Спикер уже назначен на сессию"
            )

        session_participant = SessionParticipant(
            session_id=session.id,
            user_id=user.id,
            role_id=speaker_role.id
        )

        db.add(session_participant)

        db.commit()

        if user.email:
            login_url = "http://localhost:8000/admin/login"

            await NotificationService.send_email(
                to=user.email,
                subject="Вас назначили спикером",
                template_name="speaker_invite.html",
                context={
                    "event_title": session.event.title,
                    "session_title": session.title,
                    "email": user.email,
                    "temporary_password": temporary_password,
                    "login_url": login_url
                }
            )

        return {
            "detail": "Спикер успешно назначен",
            "temporary_password": temporary_password,
            "is_new_user": is_new_user,
            "user_id": str(user.id)
        }

    @staticmethod
    def get_session_speakers(
            db: Session,
            session_id: UUID
    ):
        """
        Получение списка спикеров сессии
        """

        speaker_role_id = db.query(Role.id).filter(
            Role.name == RoleList.speaker.value
        ).scalar()

        speakers = db.query(
            SessionParticipant,
            User
        ).join(
            User,
            User.id == SessionParticipant.user_id
        ).filter(
            SessionParticipant.session_id == session_id,
            SessionParticipant.role_id == speaker_role_id
        ).all()

        items = []

        for participant, user in speakers:
            items.append({
                "id": str(user.id),
                "first_name": user.first_name,
                "second_name": user.second_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "is_temporary": user.is_temporary
            })

        return {
            "items": items,
            "total": len(items)
        }

    @staticmethod
    def remove_speaker(
            db: Session,
            session_id: UUID,
            user_id: UUID,
            current_user_id: UUID
    ):
        """
        Удаление спикера из сессии
        """

        session = db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Сессия не найдена"
            )

        organizer_role_id = db.query(Role.id).filter(
            Role.name == RoleList.organizer.value
        ).scalar()

        is_organizer = db.query(EventParticipant).filter(
            EventParticipant.event_id == session.event_id,
            EventParticipant.user_id == current_user_id,
            EventParticipant.role_id == organizer_role_id
        ).first()

        if not is_organizer:
            raise HTTPException(
                status_code=403,
                detail="Нет прав"
            )

        speaker_role_id = db.query(Role.id).filter(
            Role.name == RoleList.speaker.value
        ).scalar()

        session_participant = db.query(SessionParticipant).filter(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == user_id,
            SessionParticipant.role_id == speaker_role_id
        ).first()

        if not session_participant:
            raise HTTPException(
                status_code=404,
                detail="Спикер не найден"
            )

        db.delete(session_participant)

        db.commit()

        return {
            "detail": "Спикер удален"
        }