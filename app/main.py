from fastapi import FastAPI, HTTPException, Request
from jose import JWTError
from starlette.responses import RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

from app.api.v1.auth import router as auth_router
from app.api.v1.event import router as event_router
from app.api.v1.enum import router as enum_router
from app.api.v1.session import router as session_router
from app.api.v1.user import router as user_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.quizzes import router as quizzes_router
from app.admin.router import router as admin_router
from app.api.v1.ws import websocket_endpoint
from app.core.security import decode_token
from app.api.v1.checklists import  router as checklist_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(event_router)
app.include_router(enum_router)
app.include_router(admin_router)
app.include_router(session_router)
app.include_router(user_router)
app.include_router(feedback_router)
app.include_router(quizzes_router)
app.include_router(checklist_router)

app.add_api_websocket_route("/api/v1/ws/chat/{room_type}/{room_id}", websocket_endpoint)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="app/admin/static"), name="static")


@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401 and request.url.path.startswith("/admin"):
        return RedirectResponse(url="/admin/login")

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.get("/")
def root(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(url="/admin/login")

    try:
        decode_token(token)
        return RedirectResponse(url="/admin/dashboard")
    except JWTError:
        return RedirectResponse(url="/admin/login")
