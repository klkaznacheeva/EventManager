from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status

from app.core.enum import RoleList
from app.models import Event, Role
from app.models.chat import ChatRoom, ChatParticipant, ChatMessage
from app.models.session import Session as EventSession
from app.models.session_participant import SessionParticipant
from app.models.user import User
from app.models.event_participant import EventParticipant

class ChatService:

    # --- Базовые методы (остаются) ---
    @staticmethod
    def get_or_create_room(db: Session, session_id: UUID, room_type: str) -> ChatRoom:
        room = db.query(ChatRoom).filter(
            ChatRoom.session_id == session_id,
            ChatRoom.type == room_type
        ).first()
        if not room:
            room = ChatRoom(session_id=session_id, type=room_type)
            db.add(room)
            db.commit()
            db.refresh(room)
        return room

    @staticmethod
    def add_participant(db: Session, chat_id: UUID, user_id: UUID) -> bool:
        existing = db.query(ChatParticipant).filter(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id
        ).first()
        if existing:
            return False
        participant = ChatParticipant(chat_id=chat_id, user_id=user_id)
        db.add(participant)
        db.commit()
        return True

    @staticmethod
    def remove_participant(db: Session, chat_id: UUID, user_id: UUID) -> bool:
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id
        ).first()
        if not participant:
            return False
        db.delete(participant)
        db.commit()
        return True

    @staticmethod
    def save_message(db: Session, chat_id: UUID, user_id: UUID, message: str) -> ChatMessage:
        chat_message = ChatMessage(chat_id=chat_id, user_id=user_id, message=message)
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        return chat_message

    @staticmethod
    def get_messages(db: Session, chat_id: UUID, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        return db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).order_by(ChatMessage.created_at.asc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_user_chats(db: Session, user_id: UUID, session_id: Optional[UUID] = None) -> List[ChatRoom]:
        query = db.query(ChatRoom).join(
            ChatParticipant, ChatParticipant.chat_id == ChatRoom.id
        ).filter(ChatParticipant.user_id == user_id)
        if session_id:
            query = query.filter(ChatRoom.session_id == session_id)
        return query.all()

    @staticmethod
    def can_access_room(db: Session, user_id: UUID, chat_id: UUID) -> bool:
        # Временно для отладки
        return True

    # --- Новые методы для массового добавления участников ---
    @staticmethod
    def setup_session_rooms(db: Session, session_id: UUID):
        """Создать все три комнаты для сессии (admin, speakers, general)"""
        ChatService.get_or_create_room(db, session_id, "admin")
        ChatService.get_or_create_room(db, session_id, "speakers")
        ChatService.get_or_create_room(db, session_id, "general")

    @staticmethod
    def add_organizer_to_session(db: Session, session_id: UUID, organizer_id: UUID):
        """Добавить организатора в admin и speakers комнаты (не в general)"""
        admin_room = ChatService.get_or_create_room(db, session_id, "admin")
        speakers_room = ChatService.get_or_create_room(db, session_id, "speakers")
        ChatService.add_participant(db, admin_room.id, organizer_id)
        ChatService.add_participant(db, speakers_room.id, organizer_id)

    @staticmethod
    def add_coordinator_to_session(db: Session, session_id: UUID, coordinator_id: UUID):
        """Добавить координатора в admin и general комнаты"""
        admin_room = ChatService.get_or_create_room(db, session_id, "admin")
        general_room = ChatService.get_or_create_room(db, session_id, "general")
        ChatService.add_participant(db, admin_room.id, coordinator_id)
        ChatService.add_participant(db, general_room.id, coordinator_id)

    @staticmethod
    def add_speaker_to_session(db: Session, session_id: UUID, speaker_id: UUID):
        """Добавить спикера в speakers и general комнаты"""
        speakers_room = ChatService.get_or_create_room(db, session_id, "speakers")
        general_room = ChatService.get_or_create_room(db, session_id, "general")
        ChatService.add_participant(db, speakers_room.id, speaker_id)
        ChatService.add_participant(db, general_room.id, speaker_id)

    @staticmethod
    def add_participant_to_session(db: Session, session_id: UUID, user_id: UUID):
        """Добавить обычного участника (подписчика) только в general комнату"""
        general_room = ChatService.get_or_create_room(db, session_id, "general")
        ChatService.add_participant(db, general_room.id, user_id)

    @staticmethod
    def ensure_organizer_in_session(db: Session, session_id: UUID, organizer_id: UUID):
        """Гарантировать, что организатор добавлен (вызывать при создании сессии)"""
        ChatService.setup_session_rooms(db, session_id)
        ChatService.add_organizer_to_session(db, session_id, organizer_id)

    @staticmethod
    def get_or_create_event_room(db: Session, event_id: UUID, room_type: str):
        from app.models.event_chat import EventChatRoom
        room = db.query(EventChatRoom).filter(
            EventChatRoom.event_id == event_id,
            EventChatRoom.type == room_type
        ).first()
        if not room:
            room = EventChatRoom(event_id=event_id, type=room_type)
            db.add(room)
            db.commit()
            db.refresh(room)
        return room

    @staticmethod
    def add_event_participant(db: Session, chat_id: UUID, user_id: UUID) -> bool:
        from app.models.event_chat import EventChatParticipant
        existing = db.query(EventChatParticipant).filter(
            EventChatParticipant.chat_id == chat_id,
            EventChatParticipant.user_id == user_id
        ).first()
        if existing:
            return False
        participant = EventChatParticipant(chat_id=chat_id, user_id=user_id)
        db.add(participant)
        db.commit()
        return True

    @staticmethod
    def save_event_message(db: Session, chat_id: UUID, user_id: UUID, message: str):
        from app.models.event_chat import EventChatMessage
        chat_message = EventChatMessage(chat_id=chat_id, user_id=user_id, message=message)
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        return chat_message

    @staticmethod
    def get_event_messages(db: Session, chat_id: UUID, limit: int = 50):
        from app.models.event_chat import EventChatMessage
        return db.query(EventChatMessage).filter(
            EventChatMessage.chat_id == chat_id
        ).order_by(EventChatMessage.created_at.asc()).limit(limit).all()