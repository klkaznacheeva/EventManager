# app/services/quiz_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from uuid import UUID
from fastapi import HTTPException, status
from app.models import User, EventParticipant, Session as EventSession, Event
from app.models.quiz import Survey, Question, Answer, UserAnswer
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizSubmitRequest, QuizResultResponse, QuestionResult, QuizStatisticsResponse, UserQuizResult
from typing import List, Optional

class QuizService:

    @staticmethod
    def get_session(session_id: UUID, db: Session) -> EventSession:
        session = db.query(EventSession).filter(EventSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    @staticmethod
    def check_organizer(event_id: UUID, user_id: UUID, db: Session):
        # Проверка, что пользователь - организатор мероприятия
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event or event.organizer_id != user_id:
            raise HTTPException(status_code=403, detail="Only event organizer can manage quizzes")

    @staticmethod
    def create_quiz(data: QuizCreate, user_id: UUID, db: Session) -> Survey:
        session = QuizService.get_session(data.session_id, db)
        event_id = session.event_id
        QuizService.check_organizer(event_id, user_id, db)

        # Создаём survey типа 'quiz'
        survey = Survey(
            session_id=data.session_id,
            title=data.title,
            type="quiz",
            is_active=data.is_active
        )
        db.add(survey)
        db.flush()  # чтобы получить id

        for q_data in data.questions:
            question = Question(
                survey_id=survey.id,
                question_text=q_data.question_text,
                question_type=q_data.question_type,
                order_index=q_data.order_index
            )
            db.add(question)
            db.flush()
            # Проверка: ровно один правильный ответ
            correct_count = sum(1 for a in q_data.answers if a.is_correct)
            if correct_count != 1:
                raise HTTPException(status_code=400, detail=f"Question '{q_data.question_text}' must have exactly one correct answer")
            for a_data in q_data.answers:
                answer = Answer(
                    question_id=question.id,
                    text=a_data.text,
                    is_correct=a_data.is_correct
                )
                db.add(answer)
        db.commit()
        db.refresh(survey)
        return survey

    @staticmethod
    def update_quiz(quiz_id: UUID, data: QuizUpdate, user_id: UUID, db: Session):
        survey = db.query(Survey).filter(Survey.id == quiz_id).first()
        if not survey:
            raise HTTPException(status_code=404, detail="Quiz not found")
        session = QuizService.get_session(survey.session_id, db)
        QuizService.check_organizer(session.event_id, user_id, db)

        if data.title is not None:
            survey.title = data.title
        if data.is_active is not None:
            survey.is_active = data.is_active

        if data.questions is not None:
            # Удаляем старые вопросы и ответы (каскадно)
            db.query(Answer).filter(Answer.question_id.in_(
                db.query(Question.id).filter(Question.survey_id==quiz_id)
            )).delete(synchronize_session=False)
            db.query(Question).filter(Question.survey_id==quiz_id).delete()
            # Создаём новые
            for idx, q_data in enumerate(data.questions):
                question = Question(
                    survey_id=survey.id,
                    question_text=q_data.question_text,
                    question_type=q_data.question_type,
                    order_index=q_data.order_index
                )
                db.add(question)
                db.flush()
                correct_count = sum(1 for a in q_data.answers if a.is_correct)
                if correct_count != 1:
                    raise HTTPException(status_code=400, detail=f"Question '{q_data.question_text}' must have exactly one correct answer")
                for a_data in q_data.answers:
                    answer = Answer(
                        question_id=question.id,
                        text=a_data.text,
                        is_correct=a_data.is_correct
                    )
                    db.add(answer)
        db.commit()
        db.refresh(survey)
        return survey

    @staticmethod
    def delete_quiz(quiz_id: UUID, user_id: UUID, db: Session):
        survey = db.query(Survey).filter(Survey.id == quiz_id).first()
        if not survey:
            raise HTTPException(status_code=404, detail="Quiz not found")
        session = QuizService.get_session(survey.session_id, db)
        QuizService.check_organizer(session.event_id, user_id, db)
        db.delete(survey)
        db.commit()

    @staticmethod
    def toggle_active(quiz_id: UUID, user_id: UUID, db: Session) -> bool:
        survey = db.query(Survey).filter(Survey.id == quiz_id).first()
        if not survey:
            raise HTTPException(status_code=404, detail="Quiz not found")
        session = QuizService.get_session(survey.session_id, db)
        QuizService.check_organizer(session.event_id, user_id, db)
        survey.is_active = not survey.is_active
        db.commit()
        return survey.is_active

    @staticmethod
    def get_quizzes_by_session(session_id: UUID, user_id: UUID, db: Session) -> List[Survey]:
        session = QuizService.get_session(session_id, db)
        QuizService.check_organizer(session.event_id, user_id, db)
        quizzes = db.query(Survey).filter(Survey.session_id == session_id, Survey.type == "quiz").all()
        return quizzes

    @staticmethod
    def get_active_quiz_for_user(session_id: UUID, user_id: UUID, db: Session) -> Optional[Survey]:
        # Проверка, что пользователь является участником мероприятия
        session = db.query(EventSession).filter(EventSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        quiz = db.query(Survey).filter(
            Survey.session_id == session_id,
            Survey.type == "quiz",
            Survey.is_active == True
        ).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="No active quiz found for this session")

        # Проверка, не отвечал ли пользователь уже
        already_answered = db.query(UserAnswer).join(Question).filter(
            Question.survey_id == quiz.id,
            UserAnswer.user_id == user_id
        ).first()
        if already_answered:
            raise HTTPException(status_code=403, detail="You have already taken this quiz")

        return quiz

    @staticmethod
    def submit_quiz(quiz_id: UUID, user_id: UUID, data: QuizSubmitRequest, db: Session) -> QuizResultResponse:
        survey = db.query(Survey).filter(Survey.id == quiz_id, Survey.type == "quiz").first()
        if not survey:
            raise HTTPException(status_code=404, detail="Quiz not found")
        if not survey.is_active:
            raise HTTPException(status_code=400, detail="Quiz is not active")

        # Проверка участника
        session = QuizService.get_session(survey.session_id, db)

        # Проверка повторного прохождения
        already = db.query(UserAnswer).join(Question).filter(
            Question.survey_id == quiz_id,
            UserAnswer.user_id == user_id
        ).first()
        if already:
            raise HTTPException(status_code=400, detail="You have already submitted answers for this quiz")

        # Получаем все вопросы квиза с их правильными ответами
        questions = db.query(Question).filter(Question.survey_id == quiz_id).order_by(Question.order_index).all()
        question_map = {q.id: q for q in questions}
        # Подготовим словарь правильных ответов
        correct_answers = {}
        for q in questions:
            correct = db.query(Answer).filter(Answer.question_id == q.id, Answer.is_correct == True).first()
            if correct:
                correct_answers[q.id] = correct

        # Валидация: все переданные question_id должны принадлежать квизу, и answer_id - соответствующий вариант
        submitted_dict = {sub.question_id: sub.answer_id for sub in data.answers}
        if set(submitted_dict.keys()) != set(question_map.keys()):
            raise HTTPException(status_code=400, detail="Not all questions answered")

        # Сохраняем ответы
        for q_id, a_id in submitted_dict.items():
            # Проверка, что answer относится к вопросу
            answer = db.query(Answer).filter(Answer.id == a_id, Answer.question_id == q_id).first()
            if not answer:
                raise HTTPException(status_code=400, detail=f"Invalid answer for question {q_id}")

            user_answer = UserAnswer(
                question_id=q_id,
                user_id=user_id,
                answer_id=a_id,
                text_answer=None
            )
            db.add(user_answer)

        db.commit()

        # Подсчёт результата
        total = len(questions)
        correct_count = 0
        details = []
        for q in questions:
            user_choice_id = submitted_dict.get(q.id)
            correct_ans = correct_answers.get(q.id)
            is_correct = (user_choice_id == correct_ans.id) if correct_ans else False
            if is_correct:
                correct_count += 1
            user_answer_text = db.query(Answer).filter(Answer.id == user_choice_id).first().text
            details.append(QuestionResult(
                question_text=q.question_text,
                user_answer_text=user_answer_text,
                correct_answer_text=correct_ans.text if correct_ans else "",
                is_correct=is_correct
            ))

        percentage = (correct_count / total) * 100 if total else 0
        return QuizResultResponse(
            total_questions=total,
            correct_count=correct_count,
            percentage=percentage,
            details=details
        )

    @staticmethod
    def get_quiz_statistics(quiz_id: UUID, user_id: UUID, db: Session) -> QuizStatisticsResponse:
        survey = db.query(Survey).filter(Survey.id == quiz_id).first()
        if not survey:
            raise HTTPException(status_code=404, detail="Quiz not found")
        session = QuizService.get_session(survey.session_id, db)
        QuizService.check_organizer(session.event_id, user_id, db)

        # Получить всех пользователей, которые отвечали на этот квиз
        # Группировка по user_id
        user_answer_data = db.query(
            UserAnswer.user_id,
            func.count(UserAnswer.id).label('answers_count')
        ).join(Question).filter(Question.survey_id == quiz_id).group_by(UserAnswer.user_id).all()
        user_ids = [row.user_id for row in user_answer_data]

        results = []
        for uid in user_ids:
            # Получить количество правильных ответов
            correct_subquery = db.query(UserAnswer).join(Answer).join(Question).filter(
                Question.survey_id == quiz_id,
                UserAnswer.user_id == uid,
                Answer.is_correct == True
            ).count()
            total_questions = db.query(Question).filter(Question.survey_id == quiz_id).count()
            percentage = (correct_subquery / total_questions) * 100 if total_questions else 0
            user = db.query(User).filter(User.id == uid).first()
            # Время последнего ответа (возьмём максимальное)
            submitted_at = db.query(func.max(UserAnswer.answered_at)).filter(UserAnswer.user_id == uid).scalar()
            results.append(UserQuizResult(
                user_id=uid,
                user_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
                user_email=user.email,
                correct_count=correct_subquery,
                total_questions=total_questions,
                percentage=percentage,
                submitted_at=submitted_at
            ))

        return QuizStatisticsResponse(
            quiz_id=quiz_id,
            title=survey.title,
            total_participants=len(results),
            results=results
        )