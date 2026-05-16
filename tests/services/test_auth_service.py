# tests/services/test_auth_service.py

import pytest

from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password

from app.models.user import User

from tests.fixtures.auth_fixtures import (
    fake_register_data,
    fake_login_data
)


def test_register_success(db):

    data = fake_register_data()

    access, refresh = AuthService.register(db, data)

    assert access is not None
    assert refresh is not None

    user = UserRepository(db).get_by_email(data.email)

    assert user is not None
    assert user.email == data.email


def test_register_duplicate_email(db):

    data = fake_register_data()

    AuthService.register(db, data)

    with pytest.raises(Exception) as exc:
        AuthService.register(db, data)

    assert "Email already registered" in str(exc.value)


def test_login_success(db):

    register_data = fake_register_data()

    AuthService.register(db, register_data)

    login_data = fake_login_data()

    access, refresh, roles = AuthService.login(db, login_data)

    assert access is not None
    assert refresh is not None

    assert "user" in roles


def test_login_invalid_password(db):

    register_data = fake_register_data()

    AuthService.register(db, register_data)

    login_data = fake_login_data()
    login_data.password = "wrong_password"

    with pytest.raises(Exception) as exc:
        AuthService.login(db, login_data)

    assert "Invalid credentials" in str(exc.value)


def test_login_user_not_found(db):

    login_data = fake_login_data()

    with pytest.raises(Exception) as exc:
        AuthService.login(db, login_data)

    assert "Invalid credentials" in str(exc.value)


def test_login_admin_role(db):

    user = User(
        first_name="Admin",
        email="admin@test.com",
        password_hash=hash_password("123456"),
        is_system=True
    )

    db.add(user)
    db.commit()

    login_data = fake_login_data()

    login_data.email = "admin@test.com"

    _, _, roles = AuthService.login(db, login_data)

    assert "admin" in roles