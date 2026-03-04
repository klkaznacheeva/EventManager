from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token


class AuthService:

    @staticmethod
    def register(db: Session, data):
        repo = UserRepository(db)

        if repo.get_by_email(data.email):
            raise Exception("Email already registered")
        print(f"PASSWORD: {data.password}")
        user = repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            second_name=data.second_name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            birth_date=data.birth_date
        )

        access = create_access_token({"sub": str(user.id)})
        refresh = create_refresh_token({"sub": str(user.id)})

        return access, refresh

    @staticmethod
    def login(db: Session, data):
        repo = UserRepository(db)
        user = repo.get_by_email(data.email)

        if not user or not verify_password(data.password, user.password_hash):
            raise Exception("Invalid credentials")

        access = create_access_token({"sub": str(user.id)})
        refresh = create_refresh_token({"sub": str(user.id)})

        return access, refresh