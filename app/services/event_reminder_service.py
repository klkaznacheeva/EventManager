import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import SessionLocal
from app.models.event import Event
from app.models.session import Session as EventSession
from app.models.session_participant import SessionParticipant
from app.models.role import Role
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class EventReminderService:
    @staticmethod
    def get_events_starting_within_days(db: Session, days: int):
        """Возвращает опубликованные мероприятия, которые начнутся в течение ближайших `days` дней (включая сегодня)."""
        today = date.today()
        end_date = today + timedelta(days=days)
        events = db.query(Event).filter(
            Event.status == "published",
            func.date(Event.start_date) >= today,
            func.date(Event.start_date) <= end_date
        ).all()
        return events

    @staticmethod
    def get_speakers_for_event(db: Session, event_id: int):
        """Возвращает список уникальных спикеров мероприятия (из всех сессий)."""
        speakers = db.query(SessionParticipant).join(
            EventSession, SessionParticipant.session_id == EventSession.id
        ).filter(
            EventSession.event_id == event_id,
            SessionParticipant.role.has(Role.name == "speaker")
        ).all()
        unique = {}
        for sp in speakers:
            user = sp.user
            unique[user.id] = user
        return list(unique.values())

    @staticmethod
    async def send_reminder_to_speaker(speaker, event: Event):
        """Отправляет email спикеру с точным количеством дней до мероприятия."""
        # Вычисляем реальное количество дней до начала
        days_left = (event.start_date.date() - date.today()).days
        if days_left < 0:
            return  # мероприятие уже началось (на всякий случай)

        context = {
            "speaker_name": f"{speaker.first_name} {speaker.last_name}".strip() or speaker.email,
            "days_left": days_left,
            "event_title": event.title,
            "event_start_date": event.start_date.strftime("%d.%m.%Y %H:%M"),
            "event_end_date": event.end_date.strftime("%d.%m.%Y %H:%M") if event.end_date else "не указано",
            "event_location": event.location or "не указано",
            "organizer_email": event.organizer.email if event.organizer else "организатор",
            "event_url": f"/admin/events/{event.id}"  # относительный URL
        }
        subject = f"Напоминание: мероприятие «{event.title}» начнётся через {days_left} дней"
        await NotificationService.send_email(
            to=speaker.email,
            subject=subject,
            template_name="speaker_reminder.html",
            context=context
        )
        logger.info(f"Уведомление отправлено спикеру {speaker.email} о мероприятии {event.title} (осталось {days_left} дней)")

    @classmethod
    async def notify_speakers_for_upcoming_events(cls, days: int):
        """Основной метод: найти мероприятия, которые начнутся в течение `days` дней, и отправить уведомления спикерам."""
        db = SessionLocal()
        try:
            events = cls.get_events_starting_within_days(db, days)
            total_speakers = 0
            for event in events:
                print(f"Мероприятие: {event.title}")
                speakers = cls.get_speakers_for_event(db, event.id)
                total_speakers += len(speakers)
                for speaker in speakers:
                    print(f"* Отправляем уведомление {speaker.email}")
                    await cls.send_reminder_to_speaker(speaker, event)
            logger.info(f"Обработано {len(events)} мероприятий, отправлено уведомлений {total_speakers}")
        finally:
            db.close()