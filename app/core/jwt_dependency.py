# app/core/jwt_dependency.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
from jose import JWTError
from app.core.security import decode_token
from app.db.database import SessionLocal, get_db
from app.repositories.user_repository import UserRepository
from app.models.user import User
from sqlalchemy.orm import Session

security = HTTPBearer(auto_error=False)


async def get_current_user(
        request: Request,
        db: Session = Depends(get_db),
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Получает текущего пользователя:
    - из Authorization header
    - или из cookie
    """

    token = None

    # 1. Пытаемся взять из Authorization header
    if credentials:
        token = credentials.credentials

    # 2. Если нет — берем из cookie
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user



async def get_required_user(
        user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Обязательное получение пользователя.
    Если пользователь не авторизован - выбрасывает 401
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_optional_token(authorization: Optional[str] = None):
    """
    Получает опциональный токен из заголовка Authorization
    """
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ")[1]
    return None

async def get_current_user_ws(token: str, db: Session) -> User | None:
    from jose import JWTError, jwt
    from app.core.config import settings
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except JWTError:
        return None