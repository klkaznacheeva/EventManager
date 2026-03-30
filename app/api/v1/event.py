# app/api/v1/event.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.enum import EventStatus
from app.core.jwt_dependency import get_required_user, get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.event import (
    EventCreateRequest,
    EventUpdateRequest,
    EventListRequest,
    EventResponse,
    EventListResponse, NeedsEditRequest
)
from app.services.entity_message_service import EntityMessageService
from app.services.event_service import EventService
from starlette.responses import JSONResponse

router = APIRouter(prefix="/api/v1/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
        data: EventCreateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_required_user)
):
    """Создание нового мероприятия"""
    event = EventService.create_event(db, data, current_user.id)
    return event


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
        event_id: UUID,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Получение деталей мероприятия"""
    user_id = current_user.id if current_user else None
    event = EventService.get_event_by_id(db, event_id, user_id)
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
        event_id: UUID,
        data: EventUpdateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_required_user)
):
    """Обновление мероприятия (только для организатора)"""
    event = EventService.update_event(db, event_id, data, current_user.id)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
        event_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_required_user)
):
    """Удаление мероприятия (только для организатора)"""
    EventService.delete_event(db, event_id, current_user.id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


@router.get("/", response_model=EventListResponse)
def list_events(
        page: int = 1,
        limit: int = 20,
        category_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        start_from: Optional[str] = None,
        start_to: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Получение списка мероприятий с фильтрацией"""
    from datetime import datetime

    # Преобразуем строки в datetime если они переданы
    start_from_dt = None
    start_to_dt = None

    if start_from:
        start_from_dt = datetime.fromisoformat(start_from.replace('Z', '+00:00'))
    if start_to:
        start_to_dt = datetime.fromisoformat(start_to.replace('Z', '+00:00'))

    request = EventListRequest(
        page=page,
        limit=limit,
        category_id=category_id,
        status=status,
        search=search,
        start_from=start_from_dt,
        start_to=start_to_dt
    )

    user_id = current_user.id if current_user else None
    result = EventService.get_events_list(db, request, user_id)
    return result

@router.post("/{event_id}/reviewed")
def mark_event_reviewed(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    if not current_user.is_system:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    event = EventService.get_event_by_id(db, event_id)
    event.status = EventStatus.REVIEWED.value
    db.commit()

    return {"detail": "Event marked as reviewed"}


@router.post("/{event_id}/needs-edit")
def mark_event_needs_edit(
    event_id: UUID,
    payload: NeedsEditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    if not current_user.is_system:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    event = EventService.get_event_by_id(db, event_id)
    event.status = EventStatus.NEEDS_EDIT.value
    db.commit()

    # создаем запись в entity_messages с типом review
    EntityMessageService.create_message(
        db=db,
        entity_type="event",
        entity_id=event_id,
        type="review",
        message=payload.reason,
        author_id=current_user.id
    )

    return {"detail": "Event marked as needs edit"}