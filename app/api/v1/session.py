# app/api/v1/session.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.core.jwt_dependency import get_required_user
from app.schemas.session import (
    SessionCreateRequest,
    SessionResponse,
    SessionListResponse
)
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
