# app/admin/router.py
from uuid import UUID

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse  # Добавим для отладки
from sqlalchemy.orm import Session

from app.core.enum import RoleList
from app.core.jwt_dependency import get_required_user
from app.core.templates import render_template
from app.db.database import get_db
from app.models import User, Event, EventParticipant
from app.models.quiz import Survey
from app.models.session import Session as EventSession

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

@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, user=Depends(get_required_user)):
    context = {
        "request": request,
        "user_name": f"{user.first_name} {user.last_name}"
    }
    return render_template("profile.html", context)

@router.get("/mode-select", response_class=HTMLResponse)
def mode_select_page(request: Request, user=Depends(get_required_user)):
    context = {
        "request": request,
        "user_name": f"{user.first_name} {user.last_name}"
    }
    return render_template("mode_select.html", context)

@router.get("/profile/update", response_class=HTMLResponse)
def profile_edit_page(request: Request, user=Depends(get_required_user)):
    try:
        return render_template("profile_update.html", {"request": request})
    except Exception as e:
        import traceback
        error_text = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return PlainTextResponse(error_text, status_code=500)

@router.get("/events/{event_id}/edit", response_class=HTMLResponse)
def edit_event_page(event_id: UUID, request: Request, user=Depends(get_required_user)):
    """
    Страница редактирования мероприятия
    """
    try:
        context = {
            "request": request,
            "event_id": str(event_id),
            "user_name": f"{user.first_name} {user.last_name}",
            "user_role": "admin" if user.is_system else "organizer"
        }
        return render_template("event_edit.html", context)
    except Exception as e:
        import traceback
        error_text = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return PlainTextResponse(error_text, status_code=500)

@router.get("/events/{event_id}/sessions/{session_id}/edit", response_class=HTMLResponse)
def edit_session_page(event_id: UUID, session_id: UUID, request: Request, user=Depends(get_required_user)):
    context = {
        "request": request,
        "event_id": str(event_id),
        "session_id": str(session_id),
        "user_name": f"{user.first_name} {user.last_name}"
    }
    return render_template("session_edit.html", context)

@router.get("/sessions/{session_id}/comments", response_class=HTMLResponse)
def session_comments_page(
    request: Request,
    session_id: UUID,
    event_id: UUID,
):
    return render_template(
        "session_comments.html",
        {
            "request": request,
            "session_id": str(session_id),
            "event_id": str(event_id)
        }
    )

@router.get("/coordinator-invite/{token}", response_class=HTMLResponse)
def coordinator_invite_page(
    request: Request,
    token: str
):
    return render_template(
        "coordinator_invite.html",
        {
            "request": request,
            "token": token
        }
    )

@router.get("/events/{event_id}/coordinators", response_class=HTMLResponse)
def event_coordinators_page(
    event_id: UUID,
    request: Request,
    user=Depends(get_required_user)
):
    return render_template(
        "event_coordinators.html",
        {
            "request": request,
            "event_id": str(event_id),
            "user_name": f"{user.first_name} {user.last_name}",
            "user_role": "admin" if user.is_system else "organizer"
        }
    )

@router.get("/coordinator/tasks")
def coordinator_tasks_page(request: Request):

    return render_template(
        "coordinator_tasks.html",
        {
            "request": request
        }
    )

@router.get("/coordinator/events")
def coordinator_events_page(request: Request):

    return render_template(
        "coordinator_events.html",
        {
            "request": request
        }
    )


@router.get("/sessions/{session_id}/quizzes", response_class=HTMLResponse)
def session_quizzes_page(
        request: Request,
        session_id: UUID,
        current_user: User = Depends(get_required_user),
        db: Session = Depends(get_db)
):
    # Проверяем существование сессии
    session = db.query(EventSession).filter(EventSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    event = db.query(Event).filter(Event.id == session.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Права: организатор мероприятия или координатор
    if event.organizer_id != current_user.id:
        coord = db.query(EventParticipant).filter(
            EventParticipant.event_id == event.id,
            EventParticipant.user_id == current_user.id,
            EventParticipant.role_id == RoleList.coordinator
        ).first()
        if not coord:
            raise HTTPException(status_code=403, detail="Access denied")

    return render_template("session_quizzes.html", {"request": request, "session_id": session_id})

@router.get("/sessions/{session_id}/quiz", response_class=HTMLResponse)
def public_quiz_page(
        request: Request,
        session_id: UUID,
        current_user: User = Depends(get_required_user),
        db: Session = Depends(get_db)
):
    # Проверяем существование сессии
    session = db.query(EventSession).filter(EventSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return render_template("public_quiz.html", {"request": request, "session_id": session_id})

@router.get("/quizzes/create", response_class=HTMLResponse)
def quiz_create_page(
    request: Request,
    session_id: UUID,
    current_user: User = Depends(get_required_user),
    db: Session = Depends(get_db)
):
    # Проверка прав (аналогично session_quizzes_page)
    session = db.query(EventSession).filter(EventSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    event = db.query(Event).filter(Event.id == session.event_id).first()
    if event.organizer_id != current_user.id:
        coord = db.query(EventParticipant).filter(
            EventParticipant.event_id == event.id,
            EventParticipant.user_id == current_user.id,
            EventParticipant.role_id == RoleList.coordinator
        ).first()
        if not coord:
            raise HTTPException(status_code=403, detail="Access denied")
    return render_template("quiz_form.html", {"request": request, "session_id": session_id, "quiz": None, "title": "Создание квиза"})

@router.get("/quizzes/{quiz_id}/edit", response_class=HTMLResponse)
def quiz_edit_page(
    request: Request,
    quiz_id: UUID,
    current_user: User = Depends(get_required_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Survey).filter(Survey.id == quiz_id, Survey.type == "quiz").first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    session = db.query(EventSession).filter(EventSession.id == quiz.session_id).first()
    event = db.query(Event).filter(Event.id == session.event_id).first()
    if event.organizer_id != current_user.id:
        coord = db.query(EventParticipant).filter(
            EventParticipant.event_id == event.id,
            EventParticipant.user_id == current_user.id,
            EventParticipant.role_id == RoleList.coordinator
        ).first()
        if not coord:
            raise HTTPException(status_code=403, detail="Access denied")
    # Передаём quiz_id в шаблон, чтобы JS загрузил данные через API
    return render_template("quiz_form.html", {"request": request, "session_id": quiz.session_id, "quiz": {"id": quiz_id}, "title": "Редактирование квиза"})