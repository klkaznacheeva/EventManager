from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enum import RoleList
from app.models.role import Role


def get_role_by_name(
    db: Session,
    role_name: RoleList
):
    role = (
        db.query(Role)
        .filter(Role.name == role_name.value)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Role '{role_name.value}' not found"
        )

    return role


def get_role_id_by_name(
    db: Session,
    role_name: RoleList
):
    role = get_role_by_name(
        db,
        role_name
    )

    return role.id