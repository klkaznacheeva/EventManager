from sqlalchemy.orm import Session, joinedload
from app.models.event import Event
from app.schemas.event import EventListRequest


class EventService:

    @staticmethod
    def getList(db: Session, data: EventListRequest, token=None):

        query = db.query(Event)

        # если есть токен — подгружаем события
        if token:
            query = query.options(joinedload(Event.sessions))

        total = query.count()

        events = (
            query
            .offset((data.page - 1) * data.limit)
            .limit(data.limit)
            .all()
        )

        return {
            "items": events,
            "total": total
        }