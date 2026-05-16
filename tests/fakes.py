# =========================
# FAKE ORM ENTITIES (STABLE)
# =========================

from uuid import uuid4
from datetime import datetime


class FakeUser:
    def __init__(self, id=None, email="test@example.com", is_system=False):
        self.id = id or uuid4()
        self.first_name = "Ivan"
        self.last_name = "Petrov"
        self.email = email
        self.is_system = is_system
        self.is_active = True


class FakeCategory:
    def __init__(self, id=None):
        self.id = id or uuid4()
        self.name = "IT"
        self.description = "Tech"
        self.created_at = datetime.utcnow()


class FakeEvent:
    def __init__(self, id=None, organizer=None):
        self.id = id or uuid4()
        self.title = "Test Event"
        self.description = "Description"
        self.location = "Moscow"
        self.banner_url = "https://test.url"
        self.status = "draft"

        self.start_date = datetime.utcnow()
        self.end_date = datetime.utcnow()
        self.created_at = datetime.utcnow()

        self.category_id = uuid4()

        self.category = FakeCategory()
        self.organizer = organizer or FakeUser()

        self.participants_count = 0
        self.is_participant = False
        self.status_label = None


class FakeRole:
    def __init__(self, name="user"):
        self.id = "role-1"
        self.name = name


# =========================
# FAKE DB BUILDER (IMPORTANT)
# =========================

from unittest.mock import MagicMock


def make_db_with_events(events=None, user=None):
    db = MagicMock()

    query = MagicMock()
    db.query.return_value = query

    # chain
    query.options.return_value = query
    query.filter.return_value = query
    query.join.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query

    query.all.return_value = events or []
    query.count.return_value = len(events or [])
    query.first.return_value = events[0] if events else None

    # 🔥 ВАЖНО: user query MUST ALWAYS return FakeUser
    def fake_query(model):
        if model.__name__ == "User":
            user_query = MagicMock()
            user_query.filter.return_value.first.return_value = user
            return user_query

        return query

    db.query.side_effect = fake_query

    return db