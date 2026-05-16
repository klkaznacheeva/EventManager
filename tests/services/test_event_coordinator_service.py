from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.enum import RoleList
from app.core.helper import get_role_id_by_name
from app.models.event import Event
from app.models.event_participant import EventParticipant
from app.models.role import Role
from app.models.user import User

# EventCoordinatorService
def test_check_event_owner():
    assert True

def test_list_coordinators():
    assert True

def test_add_coordinator():
    assert True

def test_remove_coordinator():
    assert True