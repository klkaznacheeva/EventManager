from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MAIL_PROVIDER: str

    MAIL_HOST: str
    MAIL_PORT: int

    MAIL_USERNAME: str
    MAIL_PASSWORD: str

    MAIL_FROM: str
    MAIL_FROM_NAME: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()