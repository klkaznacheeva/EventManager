import asyncio
import sys
from app.services.event_reminder_service import EventReminderService

def main():
    days = 7
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print("Использование: python cli.py [days]")
            sys.exit(1)
    asyncio.run(EventReminderService.notify_speakers_for_upcoming_events(days))
    print(f"Уведомления отправлены за {days} дней.")

if __name__ == "__main__":
    main()