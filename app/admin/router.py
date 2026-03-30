# app/admin/router.py
from uuid import UUID

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse  # Добавим для отладки

from app.core.jwt_dependency import get_required_user
from app.core.templates import render_template

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render_template("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    try:
        return render_template("register.html", {"request": request})
    except Exception as e:
        import traceback
        error_text = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return PlainTextResponse(error_text, status_code=500)

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_required_user)):
    try:
        context = {"request": request, "user_name": f"{user.first_name} {user.last_name}"}
        return render_template("dashboard.html", context)
    except Exception as e:
        import traceback
        error_text = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return PlainTextResponse(error_text, status_code=500)


@router.get("/events/create", response_class=HTMLResponse)
def create_event_page(request: Request, user=Depends(get_required_user)):
    try:
        return render_template("create_event.html", {"request": request})
    except Exception as e:
        import traceback
        error_text = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return PlainTextResponse(error_text, status_code=500)


@router.get("/events/{event_id}", response_class=HTMLResponse)
def event_detail_page(
        event_id: UUID,
        request: Request,
        user=Depends(get_required_user)
):
    try:
        context = {
            "request": request,
            "user_name": f"{user.first_name} {user.last_name}",
            "user_role": "admin" if user.is_system else "organizer",
            "event_id": str(event_id)
        }
        return render_template("event_detail.html", context)
    except Exception as e:
        import traceback
        error_text = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return PlainTextResponse(error_text, status_code=500)

@router.get("/events/{event_id}/sessions/create", response_class=HTMLResponse)
def create_session_page(
    event_id: UUID,
    request: Request,
    user=Depends(get_required_user)
):
    return render_template("create_session.html", {
        "request": request,
        "event_id": str(event_id)
    })