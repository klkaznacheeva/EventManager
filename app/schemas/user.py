from datetime import date
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: UUID
    first_name: str
    second_name: Optional[str] = None
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    is_system: bool
    avatar_url: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserUpdateRequest(BaseModel):
    first_name: str
    second_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    email: EmailStr

class EmailRequest(BaseModel):
    email: EmailStr