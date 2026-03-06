from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.jwt_dependency import get_optional_token
from app.db.database import get_db
from app.schemas.event import EventListResponse, EventListRequest
from app.services.event_service import EventService

router = APIRouter(prefix="/api/v1/event", tags=["Auth"])

@router.get("/", response_model=EventListResponse)
def list(
    data: EventListRequest = Depends(),
    token: str | None = Depends(get_optional_token),
    db: Session = Depends(get_db),
):

    result = EventService.getList(db, data, token)

    return result

