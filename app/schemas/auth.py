from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import date
from uuid import UUID


class RegisterRequest(BaseModel):
    first_name: str
    second_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: str
    birth_date: date

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_roles: list[str]