# ===== Статусы для Event =====
import enum


class EventStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    reviewed = "reviewed"
    published = "published"
    needs_edit = "needs_edit"
    completed = "completed"


# ===== Статусы для Session =====
class SessionStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    reviewed = "reviewed"
    published = "published"
    completed = "completed"


class EventStatusMap:
    # ===== Локализация статусов =====
    EVENT_STATUS_LABELS = {
        EventStatus.draft: "Черновик",
        EventStatus.pending: "На проверке",
        EventStatus.reviewed: "Проверено",
        EventStatus.published: "Опубликовано",
        EventStatus.needs_edit: "Требует редактирования",
        EventStatus.completed: "Завершено",
    }

    SESSION_STATUS_LABELS = {
        SessionStatus.draft: "Черновик",
        SessionStatus.pending: "На проверке",
        SessionStatus.reviewed: "Проверено",
        SessionStatus.published: "Опубликовано",
        SessionStatus.completed: "Завершено",
    }


    # ===== Цвета для UI =====
    STATUS_COLORS = {
        "draft": "gray",
        "pending": "orange",
        "reviewed": "blue",
        "published": "green",
        "needs_edit": "red",
        "completed": "purple",
    }