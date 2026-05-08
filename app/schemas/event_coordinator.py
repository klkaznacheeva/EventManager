from uuid import UUID

from pydantic import BaseModel


class EventCoordinatorCreate(BaseModel):
    user_id: UUID