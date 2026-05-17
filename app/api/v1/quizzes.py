# app/api/v1/quizzes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.jwt_dependency import get_current_user
from app.db.database import get_db
from app.models import User
from app.models.quiz import Survey, Question, Answer
from app.services.quiz_service import QuizService
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizResponse, QuizSubmitRequest,
    QuizResultResponse, QuizStatisticsResponse, QuestionResponse, AnswerResponse
)
from typing import List

router = APIRouter(prefix="/api/v1/quizzes", tags=["quizzes"])

# Для организатора
@router.post("/sessions/{session_id}/quizzes", response_model=QuizResponse)
def create_quiz(
    session_id: UUID,
    data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = QuizService.create_quiz(data, current_user.id, db)
    # Дополнительно загрузить вопросы с ответами для ответа
    # (можно написать метод get_quiz_by_id)
    return get_quiz_response(survey, db)

@router.put("/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    quiz_id: UUID,
    data: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = QuizService.update_quiz(quiz_id, data, current_user.id, db)
    return get_quiz_response(survey, db)

@router.delete("/{quiz_id}")
def delete_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    QuizService.delete_quiz(quiz_id, current_user.id, db)
    return {"detail": "Quiz deleted"}

@router.patch("/{quiz_id}/toggle-active")
def toggle_quiz_active(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_active = QuizService.toggle_active(quiz_id, current_user.id, db)
    return {"is_active": is_active}

@router.get("/sessions/{session_id}/quizzes", response_model=List[QuizResponse])
def list_quizzes(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quizzes = QuizService.get_quizzes_by_session(session_id, current_user.id, db)
    return [get_quiz_response(q, db) for q in quizzes]

@router.get("/{quiz_id}/statistics", response_model=QuizStatisticsResponse)
def quiz_statistics(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return QuizService.get_quiz_statistics(quiz_id, current_user.id, db)

# Для участников
@router.get("/sessions/{session_id}/active-quiz", response_model=QuizResponse)
def get_active_quiz_for_user(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = QuizService.get_active_quiz_for_user(session_id, current_user.id, db)
    return get_quiz_response(survey, db)

@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
def submit_quiz(
    quiz_id: UUID,
    data: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return QuizService.submit_quiz(quiz_id, current_user.id, data, db)

# Вспомогательная функция для формирования ответа с вопросами и ответами
def get_quiz_response(survey: Survey, db: Session) -> QuizResponse:
    questions = db.query(Question).filter(Question.survey_id == survey.id).order_by(Question.order_index).all()
    q_responses = []
    for q in questions:
        answers = db.query(Answer).filter(Answer.question_id == q.id).all()
        q_responses.append(
            QuestionResponse(
                id=q.id,
                question_text=q.question_text,
                question_type=q.question_type,
                order_index=q.order_index,
                answers=[AnswerResponse(id=a.id, text=a.text, is_correct=a.is_correct) for a in answers]
            )
        )
    return QuizResponse(
        id=survey.id,
        session_id=survey.session_id,
        title=survey.title,
        type=survey.type,
        is_active=survey.is_active,
        created_at=survey.created_at,
        questions=q_responses
    )