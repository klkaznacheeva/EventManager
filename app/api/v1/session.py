# app/api/v1/session.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.enum import RoleList, EntityType, AttachmentType
from app.db.database import get_db
from app.core.jwt_dependency import get_required_user
from app.models import User, Role, EventParticipant
from app.schemas.session import (
    SessionCreateRequest,
    SessionResponse,
    SessionListResponse, SessionUpdateRequest
)
from app.services.file_service import FileService
from app.services.session_service import SessionService

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])


@router.post("/", response_model=SessionResponse)
def create_session(
        data: SessionCreateRequest,
        db: Session = Depends(get_db),
        user=Depends(get_required_user)
):
    return SessionService.create_session(db, data, user.id)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
        session_id: UUID,
        db: Session = Depends(get_db)
):
    return SessionService.get_session(db, session_id)


@router.get("/event/{event_id}", response_model=SessionListResponse)
def get_sessions_by_event(
        event_id: UUID,
        db: Session = Depends(get_db)
):
    return SessionService.get_sessions_by_event(db, event_id)


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(
        session_id: UUID,
        data: SessionUpdateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_required_user)
):
    """Редактирование сессии (только организатор)"""
    session = SessionService.get_session(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    updated_session = SessionService.update_session(db, session_id, data, current_user.id)
    return updated_session


@router.delete("/{session_id}", response_model=dict)
def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """Удаление сессии (только организатор)"""
    return SessionService.delete_session(db, session_id, current_user.id)

@router.post("/{session_id}/upload-banner")
def upload_session_banner(
    session_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """Загрузка баннера для сессии"""

    FileService.delete_files(
        db=db,
        entity_type=EntityType.SESSION,
        entity_id=session_id,
        attachment_type=AttachmentType.EVENT_COVER  # баннер сессии
    )

    db_file = FileService.save_file(
        db=db,
        file=file,
        entity_type=EntityType.SESSION,
        entity_id=session_id,
        attachment_type=AttachmentType.EVENT_COVER
    )

    return {"file_id": str(db_file.id)}

@router.post("/{session_id}/upload-file")
def upload_session_file(
    session_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """Закрепить файл к сессии"""

    db_file = FileService.save_file(
        db=db,
        file=file,
        entity_type=EntityType.SESSION,
        entity_id=session_id,
        attachment_type=AttachmentType.SESSION_FILE
    )

    return {"file_id": str(db_file.id)}