# app/schemas/quiz.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional

# Answer schemas
class AnswerBase(BaseModel):
    text: str
    is_correct: bool = False

class AnswerCreate(AnswerBase):
    pass

class AnswerResponse(AnswerBase):
    id: UUID

    class Config:
        from_attributes = True

# Question schemas
class QuestionBase(BaseModel):
    question_text: str
    question_type: str = "single_choice"
    order_index: int

class QuestionCreate(QuestionBase):
    answers: List[AnswerCreate] = Field(..., min_items=2)

class QuestionUpdate(QuestionBase):
    answers: List[AnswerCreate]

class QuestionResponse(QuestionBase):
    id: UUID
    answers: List[AnswerResponse]

    class Config:
        from_attributes = True

# Survey (Quiz) schemas
class QuizCreate(BaseModel):
    title: str
    session_id: UUID
    is_active: bool = False
    questions: List[QuestionCreate] = Field(..., min_items=1)

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    questions: Optional[List[QuestionCreate]] = None

class QuizResponse(BaseModel):
    id: UUID
    session_id: UUID
    title: str
    type: str  # 'quiz'
    is_active: bool
    created_at: datetime
    questions: List[QuestionResponse]

    class Config:
        from_attributes = True

# User answers submission
class UserAnswerSubmit(BaseModel):
    question_id: UUID
    answer_id: UUID

class QuizSubmitRequest(BaseModel):
    answers: List[UserAnswerSubmit]

# Result schemas
class QuestionResult(BaseModel):
    question_text: str
    user_answer_text: str
    correct_answer_text: str
    is_correct: bool

class QuizResultResponse(BaseModel):
    total_questions: int
    correct_count: int
    percentage: float
    details: List[QuestionResult]

# Для статистики организатора
class UserQuizResult(BaseModel):
    user_id: UUID
    user_name: str
    user_email: str
    correct_count: int
    total_questions: int
    percentage: float
    submitted_at: datetime

class QuizStatisticsResponse(BaseModel):
    quiz_id: UUID
    title: str
    total_participants: int
    results: List[UserQuizResult]