# app/api/v1/user.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.jwt_dependency import get_required_user
from app.core.security import verify_password, hash_password
from app.db.database import get_db
from app.models import User
from app.models.file_attachment import FileAttachment
from app.schemas.user import UserProfileResponse, ChangePasswordRequest, UserUpdateRequest
from app.services.file_service import FileService
from app.core.enum import EntityType, AttachmentType

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

    return UserProfileResponse(
        id=current_user.id,
        first_name=current_user.first_name,
        second_name=current_user.second_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone=current_user.phone,
        birth_date=current_user.birth_date,
        is_system=current_user.is_system,
        avatar_url=avatar_url
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