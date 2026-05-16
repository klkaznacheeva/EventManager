# app/api/v1/user.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.jwt_dependency import get_required_user
from app.core.security import verify_password, hash_password
from app.db.database import get_db
from app.models import User
from app.models.file_attachment import FileAttachment
from app.schemas.user import UserProfileResponse, ChangePasswordRequest, UserUpdateRequest, EmailRequest
from app.services.coordinator_invite_service import CoordinatorInviteService
from app.services.file_service import FileService
from app.core.enum import EntityType, AttachmentType
from app.services.notification_service import NotificationService
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_required_user)
):
    file = FileService.get_file(
        db=db,
        entity_type=EntityType.USER,
        entity_id=current_user.id,
        attachment_type=AttachmentType.AVATAR
    )

    avatar_url = f"/{file.storage_path}" if file else None

    roles = UserService.build_user_roles(db, current_user.id)

    return UserProfileResponse(
        id=current_user.id,
        first_name=current_user.first_name,
        second_name=current_user.second_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone=current_user.phone,
        birth_date=current_user.birth_date,
        is_system=current_user.is_system,
        avatar_url=avatar_url,
        roles = roles
    )


@router.post("/upload-avatar")
def upload_avatar(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user=Depends(get_required_user)
):
    FileService.delete_files(
        db=db,
        entity_type=EntityType.USER,
        entity_id=user.id,
        attachment_type=AttachmentType.AVATAR
    )

    db_file = FileService.save_file(
        db=db,
        file=file,
        entity_type=EntityType.USER,
        entity_id=user.id,
        attachment_type=AttachmentType.AVATAR
    )

    return {
        "file_id": str(db_file.id)
    }


@router.post("/change-password")
def change_password(
        data: ChangePasswordRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_required_user)
):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный старый пароль")

    user.password_hash = hash_password(data.new_password)
    db.add(user)
    db.commit()

    return {"message": "Пароль успешно изменен"}

@router.put("/profile")
def update_profile(
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_required_user)
):
    existing_user = db.query(User).filter(
        User.email == data.email,
        User.id != user.id
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже используется")

    user.first_name = data.first_name
    user.second_name = data.second_name
    user.last_name = data.last_name
    user.phone = data.phone
    user.birth_date = data.birth_date
    user.email = data.email

    db.commit()
    db.refresh(user)

    return {"message": "Профиль обновлен"}

@router.post("/coordinator-invites/{token}/accept")
def accept_coordinator_invite(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    participant = CoordinatorInviteService.accept_invite(
        db=db,
        token=token,
        user_id=current_user.id
    )

    return {
        "detail": "Coordinator invite accepted",
        "event_id": str(participant.event_id)
    }

@router.get("/search")
def search_users(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    search = f"%{query.strip()}%"

    users = (
        db.query(User)
        .filter(
            or_(
                User.email.ilike(search),
                User.phone.ilike(search),
                User.first_name.ilike(search),
                User.last_name.ilike(search)
            )
        )
        .limit(10)
        .all()
    )

    return {
        "items": [
            {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": getattr(user, "phone", None)
            }
            for user in users
        ]
    }

@router.post("/send-email")
async def send_speaker_test_email(data: EmailRequest):

    await NotificationService.send_email(
        to=data.email,
        subject="Приглашение спикера",
        template_name="speaker_invite.html",
        context={
            "event_title": "Tech Future 2026",
            "session_title": "AI и будущее образования",
            "email": data.email,
            "temporary_password": "TempPass123",
            "login_url": "http://localhost:8000/login"
        }
    )

    return {
        "detail": "Письмо отправлено"
    }