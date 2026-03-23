# app/admin/router.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse  # <- будем возвращать через templates.render

from app.core.jwt_dependency import get_required_user
from app.core.templates import templates  # объект Jinja2Templates

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_required_user)):
    # Передаем имя пользователя в шаблон
    context = {"request": request, "user_name": f"{user.first_name} {user.last_name}"}
    return templates.TemplateResponse("dashboard.html", context)