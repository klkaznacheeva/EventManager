# app/core/firebase.py
import os
import requests
import logging
from typing import Optional

PROJECT_ID = "eventmanager-b7f5c"
FCM_URL = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

# Access token из переменной окружения
FCM_ACCESS_TOKEN = os.getenv("FCM_ACCESS_TOKEN")


def send_push(fcm_token: str, title: str, body: str, data: Optional[dict] = None):
    """Отправка push-уведомления через прямой HTTP запрос"""
    print(f"📤 Отправка пуша на токен: {fcm_token[:50]}...")

    if not FCM_ACCESS_TOKEN:
        raise Exception("FCM_ACCESS_TOKEN not set in environment")

    headers = {
        "Authorization": f"Bearer {FCM_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": {
            "token": fcm_token,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    if data:
        payload["message"]["data"] = data

    response = requests.post(FCM_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Пуш отправлен! Message ID: {result.get('name')}")
        return result
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")
        raise Exception(f"FCM error: {response.text}")