from pydantic import BaseModel, Field


class CoordinatorInviteCreate(BaseModel):
    expires_in_days: int | None = Field(default=7, ge=1, le=30)