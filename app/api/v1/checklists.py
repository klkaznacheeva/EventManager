from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.database import get_db
from app.core.jwt_dependency import get_required_user
from app.models import User
from app.schemas.checklist import CompleteChecklistTaskRequest
from app.services.checklist_service import ChecklistService

router = APIRouter(prefix="/api/v1/checklists", tags=["Checklists"])

@router.patch("/{task_id}/complete")
def complete_task(
    task_id: UUID,
    data: CompleteChecklistTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_required_user)
):
    try:
        result = ChecklistService.complete_task(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            data=data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")