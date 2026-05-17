# app/models/quiz.py
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

import uuid

from app.models.base import Base


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'quiz' или 'survey'
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Question(Base):
    __tablename__ = "questions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(PG_UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, default="single_choice")
    order_index = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Answer(Base):
    __tablename__ = "answers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(PG_UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    # для одиночного выбора – один правильный вариант

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(PG_UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    answer_id = Column(PG_UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=True)
    text_answer = Column(Text, nullable=True)  # не используем для квиза, но пусть будет
    answered_at = Column(DateTime(timezone=True), server_default=func.now())