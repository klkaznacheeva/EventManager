import pytest
from uuid import uuid4
from datetime import datetime

from app.services.event_service import EventService
from app.schemas.event import EventListRequest
from tests.fakes import FakeEvent, FakeUser, make_db_with_events


@pytest.fixture(autouse=True)
def mock_roles(monkeypatch):
    monkeypatch.setattr(
        "app.core.helper.get_role_by_name",
        lambda db, role_name: type("Role", (), {"id": uuid4()})
    )

    monkeypatch.setattr(
        "app.core.helper.get_role_id_by_name",
        lambda db, role_name: uuid4()
    )


@pytest.fixture
def fake_user():
    return FakeUser(is_system=False)


@pytest.fixture
def fake_event(fake_user):
    return FakeEvent(organizer=fake_user)


@pytest.fixture
def mock_db(fake_event, fake_user):
    return make_db_with_events(
        events=[fake_event],
        user=fake_user
    )


def test_get_events_list_success(mock_db):
    request = EventListRequest(
        page=1,
        limit=10,
        category_id=None,
        status=None,
        search=None,
        start_from=None,
        start_to=None
    )

    result = EventService.get_events_list(
        db=mock_db,
        data=request,
        user_id=uuid4(),
        user_mode="participant"
    )

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].title == "Test Event"


def test_get_events_list_empty():
    db = make_db_with_events(events=[], user=None)

    request = EventListRequest(
        page=1,
        limit=10,
        category_id=None,
        status=None,
        search=None,
        start_from=None,
        start_to=None
    )

    result = EventService.get_events_list(
        db=db,
        data=request,
        user_id=None,
        user_mode="participant"
    )

    assert result.total == 0
    assert result.items == []