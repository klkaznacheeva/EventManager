from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from typing import Optional, List


# =========================================================
# CREATE TASK
# =========================================================

class CreateChecklistTaskRequest(BaseModel):
    entity_type: str
    entity_id: UUID

    title: str
    description: Optional[str] = None

    deadline: Optional[datetime] = None

    assignee_ids: List[UUID]


# =========================================================
# UPDATE TASK
# =========================================================

class UpdateChecklistTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None


# =========================================================
# COMPLETE TASK
# =========================================================

class CompleteChecklistTaskRequest(BaseModel):
    comment: Optional[str] = None


# =========================================================
# ASSIGNEE RESPONSE
# =========================================================

class ChecklistAssigneeResponse(BaseModel):
    id: UUID

    is_completed: bool
    completed_at: Optional[datetime]
    comment: Optional[str]

    user_id: UUID

    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True


# =========================================================
# TASK RESPONSE
# =========================================================

class ChecklistTaskResponse(BaseModel):
    id: UUID

    entity_type: str
    entity_id: UUID

    title: str
    description: Optional[str]

    deadline: Optional[datetime]

    created_by: Optional[UUID]

    created_at: Optional[datetime]

    completed_count: int = 0
    assignees_count: int = 0
    progress_percent: int = 0

    assignees: List[ChecklistAssigneeResponse] = []

    class Config:
        from_attributes = True


# =========================================================
# CHECKLIST LIST RESPONSE
# =========================================================

class ChecklistTaskListResponse(BaseModel):
    items: List[ChecklistTaskResponse]

    total: int
    page: int
    limit: int