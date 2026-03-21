# app/api/v1/enums.py
from fastapi import APIRouter

from app.core.enum import EnumListResponse, EnumItemResponse, EventStatusMap, EventStatus, SessionStatusMap, \
    SessionStatus

router = APIRouter(prefix="/api/v1/enums", tags=["Enums"])


@router.get("/event-statuses", response_model=EnumListResponse)
def get_event_statuses():
    """
    Получить все возможные статусы мероприятий
    """
    items = [
        EnumItemResponse(
            value=status.value,
            label=EventStatusMap.EVENT_STATUS_LABELS[status]
        )
        for status in EventStatus
    ]
    return EnumListResponse(items=items)


@router.get("/session-statuses", response_model=EnumListResponse)
def get_session_statuses():
    """
    Получить все возможные статусы сессий
    """
    items = [
        EnumItemResponse(
            value=status.value,
            label=SessionStatusMap.SESSION_STATUS_LABELS[status]
        )
        for status in SessionStatus
    ]
    return EnumListResponse(items=items)