# app/api/v1/session.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from starlette import status
from starlette.responses import Response

from app.core.enum import RoleList, EntityType, AttachmentType, SessionStatus
from app.db.database import get_db
from app.core.jwt_dependency import get_required_user
from app.models import User, Role, EventParticipant
from app.models.session_participant import SessionParticipant
from app.schemas.session import (
    SessionCreateRequest,
    SessionResponse,
    SessionListResponse, SessionUpdateRequest, SessionSpeakerResponse, SessionSpeakerCreateRequest,
    SessionSpeakerListResponse, AssignSpeakerResponse
)
from app.schemas.session_comment import SessionCommentCreate
from app.services.file_service import FileService
from app.services.session_comment_service import SessionCommentService
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

@router.delete(
    "/{session_id}/files/{file_id}"
)
def delete_session_file(
    session_id: UUID,
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """Удалить закрепленный файл сессии"""

    deleted = FileService.delete_session_file(
        db=db,
        session_id=session_id,
        file_id=file_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл сессии не найден"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{session_id}/publish")
def publish_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    session = SessionService.get_by_id(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.PUBLISHED.value

    db.commit()

    return {"detail": "Session published"}

@router.post("/{session_id}/unpublish")
def unpublish_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    session = SessionService.get_by_id(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.DRAFT.value

    db.commit()

    return {"detail": "Session unpublished"}


@router.post("/{session_id}/complete")
def complete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    session = SessionService.get_by_id(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=400,
            detail="Only published session can be completed"
        )

    session.status = SessionStatus.COMPLETED.value

    db.commit()

    return {"detail": "Session completed"}

@router.get("/{session_id}/comments")
def get_session_comments(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    comments = SessionCommentService.get_comments(
        db=db,
        session_id=session_id
    )

    items = []

    for comment in comments:
        author = comment.author

        first_name = getattr(author, "first_name", "") if author else ""
        last_name = getattr(author, "last_name", "") if author else ""
        author_name = f"{first_name} {last_name}".strip()

        items.append({
            "id": str(comment.id),
            "message": comment.message,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
            "author_id": str(comment.author_id) if comment.author_id else None,
            "author_name": author_name or "Пользователь"
        })

    return {
        "items": items
    }


@router.post("/{session_id}/comments")
def create_session_comment(
    session_id: UUID,
    model: SessionCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    comment = SessionCommentService.create_comment(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        message=model.message
    )

    return {
        "id": str(comment.id),
        "detail": "Comment created"
    }

@router.post(
    "/{session_id}/speakers",
    response_model=AssignSpeakerResponse
)
async def assign_speaker(
        session_id: UUID,
        data: SessionSpeakerCreateRequest,
        db: Session = Depends(get_db),
        user=Depends(get_required_user)
):
    return await SessionService.assign_speaker(
        db=db,
        session_id=session_id,
        data=data,
        current_user_id=user.id
    )

@router.get(
    "/{session_id}/speakers",
    response_model=SessionSpeakerListResponse
)
def get_session_speakers(
        session_id: UUID,
        db: Session = Depends(get_db),
        user=Depends(get_required_user)
):
    return SessionService.get_session_speakers(
        db=db,
        session_id=session_id
    )

@router.delete(
    "/{session_id}/speakers/{user_id}"
)
def remove_speaker(
        session_id: UUID,
        user_id: UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_required_user)
):
    return SessionService.remove_speaker(
        db=db,
        session_id=session_id,
        user_id=user_id,
        current_user_id=current_user.id
    )


@router.post("/{session_id}/join")
def join_session(
        session_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_required_user)
):
    # Проверяем существование сессии
    session = SessionService.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Сессия должна быть опубликована
    if session.status != SessionStatus.PUBLISHED.value:
        raise HTTPException(status_code=400, detail="Сессия не опубликована")

    # Проверяем, участвует ли пользователь в мероприятии (event_participants)
    event_participant = db.query(EventParticipant).filter(
        EventParticipant.event_id == session.event_id,
        EventParticipant.user_id == current_user.id
    ).first()
    if not event_participant:
        raise HTTPException(status_code=403, detail="Сначала присоединитесь к мероприятию")

    # Проверяем, не присоединён ли уже
    existing = db.query(SessionParticipant).filter(
        SessionParticipant.session_id == session_id,
        SessionParticipant.user_id == current_user.id
    ).first()
    if existing:
        return {"detail": "Already joined"}

    # Создаём запись
    participant = SessionParticipant(
        session_id=session_id,
        user_id=current_user.id,
        role_id=None  # можно не указывать, роль не нужна
    )
    db.add(participant)
    db.commit()
    return {"detail": "Joined session"}


@router.post("/{session_id}/leave")
def leave_session(
        session_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_required_user)
):
    participant = db.query(SessionParticipant).filter(
        SessionParticipant.session_id == session_id,
        SessionParticipant.user_id == current_user.id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Not joined")
    db.delete(participant)
    db.commit()
    return {"detail": "Left session"}