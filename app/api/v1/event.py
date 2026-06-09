# app/api/v1/event.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.core.enum import EventStatus, RoleList, EntityType, AttachmentType
from app.core.helper import get_role_id_by_name
from app.core.jwt_dependency import get_required_user, get_current_user
from app.db.database import get_db
from app.models import Event, EventParticipant, Role
from app.models import Session as EventSession
from app.models.session_participant import SessionParticipant
from app.models.user import User
from app.schemas.checklist import ChecklistTaskListResponse
from app.schemas.coordinator_invite import CoordinatorInviteCreate
from app.schemas.event import (
    EventCreateRequest,
    EventUpdateRequest,
    EventListRequest,
    EventResponse,
    EventListResponse, NeedsEditRequest
)
from app.schemas.event_coordinator import EventCoordinatorCreate
from app.services.checklist_service import ChecklistService
from app.services.coordinator_invite_service import CoordinatorInviteService
from app.services.entity_message_service import EntityMessageService
from app.services.event_coordinator_service import EventCoordinatorService
from app.services.event_service import EventService
from starlette.responses import JSONResponse

from app.services.file_service import FileService
from app.services.user_service import UserService

from app.models.event_participant import EventParticipant
from app.schemas.user import UserProfileResponse, UserWithRoleResponse

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

    # Получаем баннер мероприятия
    file = FileService.get_file(
        db=db,
        entity_type=EntityType.EVENT,
        entity_id=event.id,
        attachment_type=AttachmentType.EVENT_COVER
    )
    event.banner_url = f"/{file.storage_path}" if file else None
    event.participants_count = EventService.get_participants_count(db, event.id)

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
        request: Request,
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

    user_mode = request.headers.get("X-User-Mode", "organizer")

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
    result = EventService.get_events_list(db, request, user_id, user_mode)
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

@router.post("/{event_id}/publish")
def publish_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_required_user)
):
    return EventService.publish_event(
        db=db,
        event_id=event_id,
        user_id=user.id
    )

@router.post("/{event_id}/complete")
def complete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_required_user)
):
    return EventService.complete_event(
        db=db,
        event_id=event_id,
        user_id=user.id
    )

@router.post("/{event_id}/upload-banner")
def upload_event_banner(
    event_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    """Загрузка баннера для мероприятия"""

    # Удаляем старый баннер
    FileService.delete_files(
        db=db,
        entity_type=EntityType.EVENT,
        entity_id=event_id,
        attachment_type=AttachmentType.EVENT_COVER
    )

    # Сохраняем новый баннер
    db_file = FileService.save_file(
        db=db,
        file=file,
        entity_type=EntityType.EVENT,
        entity_id=event_id,
        attachment_type=AttachmentType.EVENT_COVER
    )

    return {"file_id": str(db_file.id)}


@router.post("/{event_id}/join")
def join_event(event_id: str, db: Session = Depends(get_db), user=Depends(get_required_user)):
    event = db.query(Event).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    if event.status != "published":
        raise HTTPException(status_code=400, detail="Нельзя записаться на неопубликованное мероприятие")

    EventService.join_event(db=db, event_id=UUID(event_id), user_id=user.id)
    return {"detail": "Вы успешно записались на мероприятие"}

@router.post("/{event_id}/leave")
def leave_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    EventService.leave_event(
        db=db,
        event_id=event_id,
        user_id=current_user.id
    )

    return {"detail": "Event left"}

@router.get("/{event_id}/latest-review-message")
def get_latest_review_message(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    event = EventService.get_event_by_id(db, event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Если мероприятие уже не требует редактирования,
    # актуальное сообщение в деталке не показываем
    if event.status != EventStatus.NEEDS_EDIT.value:
        return {
            "item": None
        }

    message = EntityMessageService.get_last_message(
        db=db,
        entity_type="event",
        entity_id=event_id,
        type="review"
    )

    if not message:
        return {
            "item": None
        }

    author_name = "Система"

    if message.author_id:
        author = db.query(User).filter(User.id == message.author_id).first()

        if author:
            author_name = " ".join(
                part for part in [
                    author.first_name,
                    author.last_name
                ]
                if part
            ) or author.email or "Пользователь"

    return {
        "item": {
            "id": str(message.id),
            "type": message.type,
            "message": message.message,
            "author_id": str(message.author_id) if message.author_id else None,
            "author_name": author_name,
            "created_at": message.created_at.isoformat() if message.created_at else None
        }
    }

@router.post("/{event_id}/submit-review")
def submit_event_for_review(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    event = EventService.get_event_by_id(db, event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    if current_user.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot submit event for review"
        )

    if str(event.organizer_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can submit only your own event"
        )

    allowed_statuses = [
        EventStatus.DRAFT.value,
        EventStatus.NEEDS_EDIT.value
    ]

    if event.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event can be submitted for review only from draft or needs_edit status"
        )

    event.status = EventStatus.PENDING.value
    db.commit()
    db.refresh(event)

    return {
        "detail": "Event submitted for review",
        "status": event.status
    }

@router.post("/{event_id}/coordinator-invite")
def create_coordinator_invite(
    event_id: UUID,
    model: CoordinatorInviteCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    invite = CoordinatorInviteService.create_invite(
        db=db,
        event_id=event_id,
        current_user_id=current_user.id,
        expires_in_days=model.expires_in_days
    )

    base_url = str(request.base_url).rstrip("/")

    invite_url = f"{base_url}/admin/coordinator-invite/{invite.token}"

    return {
        "id": str(invite.id),
        "event_id": str(invite.event_id),
        "token": invite.token,
        "invite_url": invite_url,
        "is_active": invite.is_active,
        "expires_at": invite.expires_at.isoformat() if invite.expires_at else None,
        "created_at": invite.created_at.isoformat() if invite.created_at else None
    }

@router.get("/{event_id}/coordinators")
def get_event_coordinators(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    rows = EventCoordinatorService.list_coordinators(
        db=db,
        event_id=event_id,
        current_user_id=current_user.id
    )

    items = []

    for participant, user in rows:
        items.append({
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": getattr(user, "phone", None)
        })

    return {"items": items}


@router.post("/{event_id}/coordinators")
def add_event_coordinator(
    event_id: UUID,
    model: EventCoordinatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    EventCoordinatorService.add_coordinator(
        db=db,
        event_id=event_id,
        user_id=model.user_id,
        current_user_id=current_user.id
    )

    return {
        "detail": "Coordinator added"
    }


@router.delete("/{event_id}/coordinators/{user_id}")
def remove_event_coordinator(
    event_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    EventCoordinatorService.remove_coordinator(
        db=db,
        event_id=event_id,
        user_id=user_id,
        current_user_id=current_user.id
    )

    return {
        "detail": "Coordinator removed"
    }

@router.get(
    "/{event_id}/coordinators/{user_id}/tasks",
    summary="Получение чек листов по пользователю"
)
def get_coordinator_tasks(
        event_id: UUID,
        user_id: UUID,

        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return ChecklistService.get_coordinator_tasks(
        db=db,
        event_id=event_id,
        user_id=user_id
    )

@router.post(
    "/{event_id}/coordinators/{user_id}/tasks",
    summary="Создания чек-листов для координатора"
)
def create_coordinator_tasks(
        event_id: UUID,
        user_id: UUID,
        data: dict,

        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return ChecklistService.create_coordinator_tasks(
        db=db,
        event_id=event_id,
        user_id=user_id,
        tasks=data.get("tasks", []),
        current_user_id=current_user.id
    )

@router.get(
    "/tasks/my",
    summary="АПИ для получения моих задач по мероприятиям",
    response_model=ChecklistTaskListResponse
)
def get_my_tasks(
        page: int = Query(1),
        limit: int = Query(20),

        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return ChecklistService.get_my_tasks(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit
    )


@router.get("/coordinator/events")
def get_coordinator_events(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return EventService.get_coordinator_events(
        db=db,
        user_id=current_user.id
    )


@router.get("/{event_id}/participants", response_model=List[UserWithRoleResponse])
def get_event_participants(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    # Проверка прав (организатор или координатор мероприятия)
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    if event.organizer_id != current_user.id:
        coord_role_id = get_role_id_by_name(db, RoleList.coordinator)
        coord = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == current_user.id,
            EventParticipant.role_id == coord_role_id
        ).first()
        if not coord:
            raise HTTPException(403, "Access denied")

    # Получаем всех участников (записи в event_participants)
    participants = db.query(EventParticipant).filter(EventParticipant.event_id == event_id).all()
    user_ids = [p.user_id for p in participants]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: u for u in users}

    # ID ролей
    coord_role_id = get_role_id_by_name(db, RoleList.coordinator)
    organizer_role_id = get_role_id_by_name(db, RoleList.organizer)

    # Определяем спикеров (через сессии)
    sessions = db.query(EventSession).filter(EventSession.event_id == event_id).all()
    session_ids = [s.id for s in sessions]
    speaker_ids = set()
    if session_ids:
        speakers = db.query(SessionParticipant).filter(
            SessionParticipant.session_id.in_(session_ids),
            SessionParticipant.role.has(name=RoleList.speaker.value)
        ).all()
        speaker_ids = {sp.user_id for sp in speakers}

    result = []
    for p in participants:
        u = user_map.get(p.user_id)
        if not u:
            continue
        is_coord = (p.role_id == coord_role_id)
        is_organizer = (p.role_id == organizer_role_id)
        is_speaker = (u.id in speaker_ids)

        avatar = FileService.get_file(db, EntityType.USER, u.id, AttachmentType.AVATAR)
        avatar_url = f"/{avatar.storage_path}" if avatar else None

        result.append(UserWithRoleResponse(
            id=u.id,
            first_name=u.first_name,
            second_name=u.second_name,
            last_name=u.last_name,
            email=u.email,
            phone=u.phone,
            birth_date=u.birth_date,
            is_system=u.is_system,
            avatar_url=avatar_url,
            roles=UserService.build_user_roles(db, u.id),
            is_speaker=is_speaker,
            is_coordinator=is_coord,
            is_organizer=is_organizer
        ))
    return result

@router.post("/{event_id}/participants/{user_id}/make-organizer")
def make_organizer(
    event_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(403, "Only main organizer can assign co-organizers")

    coordinator_role_id = get_role_id_by_name(db, RoleList.coordinator)
    organizer_role_id = get_role_id_by_name(db, RoleList.organizer)

    participant = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == user_id
    ).first()
    if not participant:
        raise HTTPException(404, "Participant not found")

    if participant.role_id != coordinator_role_id:
        raise HTTPException(400, "Only coordinators can be promoted to organizer")

    participant.role_id = organizer_role_id
    db.commit()
    return {"detail": "User promoted to co-organizer"}

@router.post("/{event_id}/participants/{user_id}/revoke-organizer")
def revoke_organizer(
    event_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(403, "Only main organizer can revoke co-organizer rights")

    coordinator_role_id = get_role_id_by_name(db, RoleList.coordinator)
    organizer_role_id = get_role_id_by_name(db, RoleList.organizer)

    participant = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == user_id
    ).first()
    if not participant:
        raise HTTPException(404, "Participant not found")

    if participant.role_id != organizer_role_id:
        raise HTTPException(400, "User is not an organizer")

    participant.role_id = coordinator_role_id
    db.commit()
    return {"detail": "User demoted to coordinator"}