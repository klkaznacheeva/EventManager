from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.db.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    access, refresh = AuthService.register(db, data)
    return TokenResponse(access_token=access, refresh_token=refresh, user_roles=[])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    access, refresh, roles = AuthService.login(db, data)
    return TokenResponse(access_token=access, refresh_token=refresh, user_roles=roles)

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}