from datetime import date
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: UUID
    first_name: str
    second_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: date
    is_system: bool
    avatar_url: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str