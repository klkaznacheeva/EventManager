# app/repositories/event_repository.py
from sqlalchemy.orm import Session
from app.models.event import Event
from typing import Optional
from uuid import UUID


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, event_id: UUID) -> Optional[Event]:
        return self.db.query(Event).filter(Event.id == event_id).first()

    def create(self, **kwargs) -> Event:
        event = Event(**kwargs)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update(self, event: Event, **kwargs) -> Event:
        for key, value in kwargs.items():
            setattr(event, key, value)
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, event: Event) -> None:
        self.db.delete(event)
        self.db.commit()