# app/admin/router.py
from uuid import UUID

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse  # <- будем возвращать через templates.render

from app.core.jwt_dependency import get_required_user
from app.core.templates import templates  # объект Jinja2Templates

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_required_user)):
    # Передаем имя пользователя в шаблон
    context = {"request": request, "user_name": f"{user.first_name} {user.last_name}"}
    return templates.TemplateResponse("dashboard.html", context)

@router.get("/events/create", response_class=HTMLResponse)
def create_event_page(request: Request, user=Depends(get_required_user)):
    return templates.TemplateResponse("create_event.html", {"request": request})

@router.get("/events/{event_id}", response_class=HTMLResponse)
def event_detail_page(
    event_id: UUID,
    request: Request,
    user=Depends(get_required_user)
):
    """
    Страница детального просмотра мероприятия.
    Данные мероприятия подгружаются через JS с API /api/v1/events/{event_id}
    """
    context = {
        "request": request,
        "user_name": f"{user.first_name} {user.last_name}",
        "user_role": "admin" if user.is_system else "organizer",
        "event_id": str(event_id)
    }

    return templates.TemplateResponse("event_detail.html", context)