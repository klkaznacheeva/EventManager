from pydantic import BaseModel, Field


class SessionCommentCreate(BaseModel):
    message: str = Field(..., min_length=1)