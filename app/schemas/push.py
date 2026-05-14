from typing import Optional
from pydantic import BaseModel, Field


class BindPushTokenRequest(BaseModel):
    code: str
    fcm_token: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None

class TestPushRequest(BaseModel):
    fcm_token: str
    title: str = "Тестовое уведомление"
    body: str = "Это тестовый push"