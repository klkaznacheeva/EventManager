from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional
from uuid import UUID
from datetime import date


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(
        self,
        first_name: str,
        email: str,
        password_hash: str,
        last_name: Optional[str] = None,
        second_name: Optional[str] = None,
        phone: Optional[str] = None,
        birth_date: Optional[date] = None,
    ) -> User:
        print(f"Password length: {len(password_hash)} chars, {len(password_hash.encode('utf-8'))} bytes")

        user = User(
            first_name=first_name,
            second_name=second_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            birth_date=birth_date,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user