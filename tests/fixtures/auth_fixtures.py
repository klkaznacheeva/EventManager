# tests/fixtures/auth_fixtures.py

from types import SimpleNamespace


def fake_register_data():

    return SimpleNamespace(
        first_name="Ivan",
        last_name="Ivanov",
        second_name="Ivanovich",
        email="ivan@test.com",
        phone="+79999999999",
        password="123456",
        birth_date=None
    )


def fake_login_data():

    return SimpleNamespace(
        email="ivan@test.com",
        password="123456"
    )