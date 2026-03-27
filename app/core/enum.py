from typing import List

from pydantic import BaseModel

import enum


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    NEEDS_EDIT = "needs_edit"
    COMPLETED = "completed"

class SessionStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    COMPLETED = "completed"


class EventStatusMap:
    EVENT_STATUS_LABELS = {
        EventStatus.DRAFT: "Черновик",
        EventStatus.PENDING: "На проверке",
        EventStatus.REVIEWED: "Проверено",
        EventStatus.PUBLISHED: "Опубликовано",
        EventStatus.NEEDS_EDIT: "Требует редактирования",
        EventStatus.COMPLETED: "Завершено",
    }


class SessionStatusMap:
    SESSION_STATUS_LABELS = {
        SessionStatus.DRAFT: "Черновик",
        SessionStatus.PENDING: "На проверке",
        SessionStatus.REVIEWED: "Проверено",
        SessionStatus.PUBLISHED: "Опубликовано",
        SessionStatus.COMPLETED: "Завершено",
    }


class EnumItemResponse(BaseModel):
    value: str
    label: str

class EnumListResponse(BaseModel):
    items: List[EnumItemResponse]

class RoleList(str, enum.Enum):
    admin = "admin"
    organizer = "organizer"
    coordinator = "coordinator"
    user = "user"