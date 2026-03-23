from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.jwt_dependency import get_required_user
from app.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserProfileResponse
from app.services.auth_service import AuthService
from app.db.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    access, refresh = AuthService.register(db, data)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    access, refresh = AuthService.login(db, data)
    return TokenResponse(access_token=access, refresh_token=refresh)

@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_required_user)):
    return UserProfileResponse(
        id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        is_system=current_user.is_system
    )