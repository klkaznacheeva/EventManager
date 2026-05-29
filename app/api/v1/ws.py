import json
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.jwt_dependency import get_current_user_ws
from app.models import User
from app.services.chat_service import ChatService

active_connections = {}

async def websocket_endpoint(
    websocket: WebSocket,
    room_type: str,   # 'event_coordinators', 'session_speakers', 'session_general'
    room_id: str,     # UUID мероприятия (для event_coordinators) или сессии
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    user = await get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # Временно разрешаем все типы (позже заменим на проверку прав)
    allowed = room_type in ("event_coordinators", "session_speakers", "session_general")
    if not allowed:
        await websocket.close(code=1003, reason="Access denied")
        return

    await websocket.accept()
    key = f"{room_type}:{room_id}"
    if key not in active_connections:
        active_connections[key] = set()
    active_connections[key].add(websocket)

    # --- Определяем, какую модель чата использовать ---
    if room_type == "event_coordinators":
        chat_room = ChatService.get_or_create_event_room(db, UUID(room_id), "coordinators")
        ChatService.add_event_participant(db, chat_room.id, user.id)
        messages = ChatService.get_event_messages(db, chat_room.id, limit=50)
        if messages:
            user_ids = list(set(msg.user_id for msg in messages))
            users = db.query(User).filter(User.id.in_(user_ids)).all()
            user_map = {u.id: f"{u.first_name} {u.last_name}".strip() or u.email for u in users}
            for msg in messages:
                await websocket.send_json({
                    "type": "history",
                    "id": str(msg.id),
                    "user_id": str(msg.user_id),
                    "user_name": user_map.get(msg.user_id, str(msg.user_id)),
                    "message": msg.message,
                    "created_at": msg.created_at.isoformat()
                })
    else:
        # Работа с session-чатами (общие таблицы)
        # Определяем тип комнаты для session-чатов
        if room_type == "session_speakers":
            chat_type = "speakers"
        else:  # session_general
            chat_type = "general"
        chat_room = ChatService.get_or_create_room(db, UUID(room_id), chat_type)
        ChatService.add_participant(db, chat_room.id, user.id)
        messages = ChatService.get_messages(db, chat_room.id, limit=50)
        # Для session-чатов нужно подтянуть имена пользователей
        user_ids = list(set(msg.user_id for msg in messages))
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        user_map = {u.id: f"{u.first_name} {u.last_name}".strip() or u.email for u in users}
        for msg in messages:
            await websocket.send_json({
                "type": "history",
                "id": str(msg.id),
                "user_id": str(msg.user_id),
                "user_name": user_map.get(msg.user_id, str(msg.user_id)),
                "message": msg.message,
                "created_at": msg.created_at.isoformat()
            })

    # Приветствие
    await websocket.send_json({"type": "connected", "message": f"Connected to {room_type} chat"})

    try:
        while True:
            data = await websocket.receive_text()
            try:
                json_data = json.loads(data)
                message_text = json_data.get("message")
                if not message_text:
                    continue

                # Сохраняем сообщение в зависимости от типа комнаты
                if room_type == "event_coordinators":
                    saved = ChatService.save_event_message(db, chat_room.id, user.id, message_text)
                    # Для рассылки используем user_name из объекта user
                    broadcast_data = {
                        "type": "message",
                        "id": str(saved.id),
                        "user_id": str(user.id),
                        "user_name": f"{user.first_name} {user.last_name}".strip() or user.email,
                        "message": saved.message,
                        "created_at": saved.created_at.isoformat()
                    }
                else:
                    saved = ChatService.save_message(db, chat_room.id, user.id, message_text)
                    broadcast_data = {
                        "type": "message",
                        "id": str(saved.id),
                        "user_id": str(user.id),
                        "user_name": f"{user.first_name} {user.last_name}".strip() or user.email,
                        "message": saved.message,
                        "created_at": saved.created_at.isoformat()
                    }

                # Рассылаем всем в комнате
                for conn in active_connections.get(key, set()):
                    try:
                        await conn.send_json(broadcast_data)
                    except:
                        pass
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    except WebSocketDisconnect:
        if key in active_connections:
            active_connections[key].discard(websocket)
            if not active_connections[key]:
                del active_connections[key]