# tests/conftest.py
from unittest.mock import MagicMock

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Event, Role, User
from app.models.base import Base
from tests.fakes import FakeUser

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_db(fake_event):
    db = MagicMock()

    query = MagicMock()

    # chain
    query.options.return_value = query
    query.join.return_value = query
    query.filter.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.order_by.return_value = query

    query.all.return_value = [fake_event]
    query.count.return_value = 1
    query.first.return_value = fake_event

    # 🔥 FIXED DB QUERY ROUTING
    def query_side_effect(model):
        model_name = getattr(model, "__name__", None)

        # USER FIX
        if model_name == "User":
            user_query = MagicMock()

            user_query.filter.return_value.first.return_value = FakeUser(
                id="user-1",
                email="test@mail.com",
                is_system=False
            )

            return user_query

        # EVENT
        if model_name == "Event":
            return query

        # ROLE
        if model_name == "Role":
            role_query = MagicMock()
            role_query.filter.return_value.scalar.return_value = "role-1"
            return role_query

        return query

        # -------------------------
        # EVENT QUERY
        # -------------------------
        if model is Event:
            return query

        # -------------------------
        # ROLE QUERY
        # -------------------------
        if model is Role:
            role_query = MagicMock()
            role_query.filter.return_value.scalar.return_value = "role-1"
            return role_query

        return query

    db.query.side_effect = query_side_effect

    return db