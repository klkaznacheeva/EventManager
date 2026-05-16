from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.checklist import (
    CreateChecklistTaskRequest,
    ChecklistTaskListResponse,
    ChecklistTaskResponse,
    CompleteChecklistTaskRequest
)

from app.services.checklist_service import ChecklistService

from app.core.jwt_dependency import get_current_user


router = APIRouter(
    prefix="/checklists",
    tags=["Checklist"]
)


# =========================================================
# CREATE TASK
# =========================================================

@router.post(
    "",
    response_model=ChecklistTaskResponse
)
def create_checklist_task(
        data: CreateChecklistTaskRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    try:

        return ChecklistService.create_task(
            db=db,
            data=data,
            current_user_id=current_user.id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================================================
# ENTITY TASKS
# =========================================================

@router.get(
    "/entity",
    response_model=ChecklistTaskListResponse
)
def get_entity_tasks(
        entity_type: str = Query(...),
        entity_id: UUID = Query(...),

        page: int = Query(1),
        limit: int = Query(20),

        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return ChecklistService.get_entity_tasks(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        page=page,
        limit=limit
    )


# =========================================================
# MY TASKS
# =========================================================

@router.get(
    "/my",
    response_model=ChecklistTaskListResponse
)
def get_my_tasks(
        page: int = Query(1),
        limit: int = Query(20),

        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return ChecklistService.get_my_tasks(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit
    )


# =========================================================
# COMPLETE TASK
# =========================================================

@router.patch(
    "/{task_id}/complete"
)
def complete_task(
        task_id: UUID,
        data: CompleteChecklistTaskRequest,

        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    try:

        return ChecklistService.complete_task(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            data=data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================================================
# DELETE TASK
# =========================================================

@router.delete(
    "/{task_id}"
)
def delete_task(
        task_id: UUID,

        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    try:

        return ChecklistService.delete_task(
            db=db,
            task_id=task_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )