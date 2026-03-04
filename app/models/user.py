from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    first_name = Column(String(100), nullable=False)
    second_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    phone = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        onupdate=func.now(),
        nullable=True
    )