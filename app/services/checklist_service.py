from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.checklist_task import ChecklistTask
from app.models.checklist_task_assignee import ChecklistTaskAssignee

from app.models.event import Event
from app.models.session import Session as EventSession

from app.schemas.checklist import (
    CreateChecklistTaskRequest,
    ChecklistTaskListResponse,
    ChecklistTaskResponse,
    ChecklistAssigneeResponse,
    CompleteChecklistTaskRequest
)


class ChecklistService:

    # =========================================================
    # CREATE TASK
    # =========================================================

    @staticmethod
    def create_task(
            db: Session,
            data: CreateChecklistTaskRequest,
            current_user_id: UUID
    ) -> ChecklistTaskResponse:

        # ---------------------------------------------------------
        # VALIDATE ENTITY
        # ---------------------------------------------------------

        if data.entity_type == "event":

            entity = (
                db.query(Event)
                .filter(Event.id == data.entity_id)
                .first()
            )

        elif data.entity_type == "session":

            entity = (
                db.query(EventSession)
                .filter(EventSession.id == data.entity_id)
                .first()
            )

        else:
            raise ValueError("Invalid entity_type")

        if not entity:
            raise ValueError("Entity not found")

        # ---------------------------------------------------------
        # CREATE TASK
        # ---------------------------------------------------------

        task = ChecklistTask(
            entity_type=data.entity_type,
            entity_id=data.entity_id,

            title=data.title,
            description=data.description,

            deadline=data.deadline,

            created_by=current_user_id,

            created_at=datetime.utcnow()
        )

        db.add(task)
        db.flush()

        # ---------------------------------------------------------
        # CREATE ASSIGNEES
        # ---------------------------------------------------------

        for assignee_id in data.assignee_ids:

            assignment = ChecklistTaskAssignee(
                task_id=task.id,
                user_id=assignee_id,

                created_at=datetime.utcnow()
            )

            db.add(assignment)

        db.commit()

        return ChecklistService._build_task_response(task)

    # =========================================================
    # GET ENTITY TASKS
    # =========================================================

    @staticmethod
    def get_entity_tasks(
            db: Session,
            entity_type: str,
            entity_id: UUID,
            page: int = 1,
            limit: int = 20
    ) -> ChecklistTaskListResponse:

        query = (
            db.query(ChecklistTask)
            .options(
                joinedload(ChecklistTask.assignees)
                .joinedload(ChecklistTaskAssignee.user)
            )
            .filter(
                ChecklistTask.entity_type == entity_type,
                ChecklistTask.entity_id == entity_id
            )
            .order_by(ChecklistTask.created_at.desc())
        )

        total = query.count()

        tasks = (
            query.offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        items = [
            ChecklistService._build_task_response(task)
            for task in tasks
        ]

        return ChecklistTaskListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit
        )

    # =========================================================
    # GET MY TASKS
    # =========================================================

    @staticmethod
    def get_my_tasks(
            db: Session,
            user_id: UUID,
            page: int = 1,
            limit: int = 20
    ) -> ChecklistTaskListResponse:

        query = (
            db.query(ChecklistTask)
            .join(ChecklistTask.assignees)
            .options(
                joinedload(ChecklistTask.assignees)
                .joinedload(ChecklistTaskAssignee.user)
            )
            .filter(
                ChecklistTaskAssignee.user_id == user_id
            )
            .order_by(ChecklistTask.deadline.asc())
        )

        total = query.count()

        tasks = (
            query.offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        items = [
            ChecklistService._build_task_response(task)
            for task in tasks
        ]

        return ChecklistTaskListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit
        )

    # =========================================================
    # COMPLETE TASK
    # =========================================================

    @staticmethod
    def complete_task(
            db: Session,
            task_id: UUID,
            user_id: UUID,
            data: CompleteChecklistTaskRequest
    ):

        assignment = (
            db.query(ChecklistTaskAssignee)
            .filter(
                ChecklistTaskAssignee.task_id == task_id,
                ChecklistTaskAssignee.user_id == user_id
            )
            .first()
        )

        if not assignment:
            raise ValueError("Task assignment not found")

        assignment.is_completed = True
        assignment.completed_at = datetime.utcnow()
        assignment.comment = data.comment

        db.commit()

        return {
            "message": "Task completed"
        }

    # =========================================================
    # DELETE TASK
    # =========================================================

    @staticmethod
    def delete_task(
            db: Session,
            task_id: UUID
    ):

        task = (
            db.query(ChecklistTask)
            .filter(ChecklistTask.id == task_id)
            .first()
        )

        if not task:
            raise ValueError("Task not found")

        db.delete(task)

        db.commit()

        return {
            "message": "Task deleted"
        }

    # =========================================================
    # RESPONSE BUILDER
    # =========================================================

    @staticmethod
    def _build_task_response(
            task: ChecklistTask
    ) -> ChecklistTaskResponse:

        assignees = []

        completed_count = 0

        for assignment in task.assignees:

            if assignment.is_completed:
                completed_count += 1

            assignees.append(
                ChecklistAssigneeResponse(
                    id=assignment.id,

                    is_completed=assignment.is_completed,
                    completed_at=assignment.completed_at,
                    comment=assignment.comment,

                    user_id=assignment.user.id,

                    first_name=assignment.user.first_name,
                    last_name=assignment.user.last_name,
                    email=assignment.user.email
                )
            )

        assignees_count = len(task.assignees)

        progress_percent = 0

        if assignees_count > 0:
            progress_percent = int(
                (completed_count / assignees_count) * 100
            )

        return ChecklistTaskResponse(
            id=task.id,

            entity_type=task.entity_type,
            entity_id=task.entity_id,

            title=task.title,
            description=task.description,

            deadline=task.deadline,

            created_by=task.created_by,

            created_at=task.created_at,

            completed_count=completed_count,
            assignees_count=assignees_count,
            progress_percent=progress_percent,

            assignees=assignees
        )