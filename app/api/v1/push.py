# app/api/v1/push.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.core.jwt_dependency import get_required_user
from app.models.user import User
from app.models.push_subscription import PushSubscription

router = APIRouter(prefix="/api/v1/push", tags=["Push"])


class SaveTokenRequest(BaseModel):
    fcm_token: str
    device_name: Optional[str] = "Browser"
    device_type: Optional[str] = "web"


@router.post("/save-token")
def save_fcm_token(
        request: SaveTokenRequest,
        current_user: User = Depends(get_required_user),
        db: Session = Depends(get_db)
):
    """
    Сохраняет FCM токен пользователя.
    Вызывается из браузера или мобильного приложения.
    """

    # Проверяем, существует ли уже такой токен
    existing = db.query(PushSubscription).filter(
        PushSubscription.fcm_token == request.fcm_token
    ).first()

    if existing:
        # Обновляем существующую запись
        existing.user_id = current_user.id
        existing.device_name = request.device_name
        existing.device_type = request.device_type
        existing.is_active = True
        existing.updated_at = datetime.utcnow()
        db.commit()
        return {"detail": "Token updated successfully"}

    # Создаём новую запись
    subscription = PushSubscription(
        user_id=current_user.id,
        fcm_token=request.fcm_token,
        device_name=request.device_name,
        device_type=request.device_type
    )
    db.add(subscription)
    db.commit()

    return {"detail": "Token saved successfully"}


class SendPushRequest(BaseModel):
    title: str
    body: str
    fcm_token: Optional[str] = None  # если не указан, отправляем на все устройства пользователя

class SendTestPushRequest(BaseModel):
    fcm_token: str
    title: str = "Тестовое уведомление"
    body: str = "Это тестовый push"

@router.post("/send-test")
def send_test_push_direct(
        request: SendTestPushRequest,
        current_user: User = Depends(get_required_user),
        db: Session = Depends(get_db)
):
    """Отправка тестового пуша"""
    from app.core.firebase import send_push

    print(f"🔍 Received send-test request")
    print(f"🔍 Token: {request.fcm_token[:50]}...")
    print(f"🔍 Title: {request.title}")

    try:
        result = send_push(
            fcm_token=request.fcm_token,
            title=request.title,
            body=request.body,
            data={"type": "test", "user_id": str(current_user.id)}
        )
        return {"success": True, "message_id": result}
    except Exception as e:
        print(f"❌ Error in send-test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-test-curl")
def send_test_curl(
        current_user: User = Depends(get_required_user),
        db: Session = Depends(get_db)
):
    """Отправляет пуш через прямой HTTP запрос (как cURL)"""
    import requests
    import os

    # Токен из БД (последний активный)
    token_record = db.query(PushSubscription).filter(
        PushSubscription.user_id == current_user.id,
        PushSubscription.is_active == True
    ).order_by(PushSubscription.created_at.desc()).first()

    if not token_record:
        raise HTTPException(status_code=404, detail="No token found")

    fcm_token = token_record.fcm_token

    # Access token нужно получить заранее и сохранить в переменную окружения
    access_token = os.getenv("FCM_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(status_code=500, detail="FCM_ACCESS_TOKEN not set")

    project_id = "eventmanager-b7f5c"
    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": {
            "token": fcm_token,
            "notification": {
                "title": "Тест через прямой HTTP",
                "body": "Пуш отправлен как в cURL"
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()