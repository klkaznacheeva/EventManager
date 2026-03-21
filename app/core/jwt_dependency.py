# app/core/jwt_dependency.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
from jose import JWTError
from app.core.security import decode_token
from app.db.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.models.user import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Получает текущего пользователя из токена.
    Если токен не предоставлен - возвращает None
    Если токен невалидный - выбрасывает 401
    """
    if not credentials:
        return None

    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    finally:
        db.close()


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