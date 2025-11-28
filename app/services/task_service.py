# app/services/task_service.py
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.interfaces.task_service import ITaskService
from app.domain.models.db_models import TaskDB
from app.domain.models.tasks import Task, TaskType, TaskStatus


class TaskService(ITaskService):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_task(
        self,
        session_id: str,
        agent_id: str,
        title: str,
        description: str,
        task_type: TaskType,
    ) -> Task:
        task_id = str(uuid.uuid4())
        db_obj = TaskDB(
            id=task_id,
            session_id=session_id,
            agent_id=agent_id,
            type=task_type,
            title=title,
            description=description,
        )
        self._session.add(db_obj)
        await self._session.commit()
        await self._session.refresh(db_obj)
        return Task.model_validate(db_obj)

    async def update_task(self, task: Task) -> Task:
        stmt = select(TaskDB).where(TaskDB.id == task.id)
        result = await self._session.exec(stmt)
        db_obj = result.one()
        db_obj.status = task.status
        db_obj.updated_at = datetime.utcnow()
        db_obj.result = task.result
        db_obj.error = task.error
        await self._session.commit()
        await self._session.refresh(db_obj)
        return Task.model_validate(db_obj)

    async def get_task(self, task_id: str) -> Task:
        stmt = select(TaskDB).where(TaskDB.id == task_id)
        result = await self._session.exec(stmt)
        db_obj = result.one()
        return Task.model_validate(db_obj)

    async def list_tasks_for_session(self, session_id: str) -> Sequence[Task]:
        stmt = select(TaskDB).where(TaskDB.session_id == session_id)
        result = await self._session.exec(stmt)
        rows = result.all()
        return [Task.model_validate(r) for r in rows]

    async def set_status(
        self, task_id: str, status: TaskStatus, error: str | None = None
    ) -> Task:
        stmt = select(TaskDB).where(TaskDB.id == task_id)
        result = await self._session.exec(stmt)
        db_obj = result.one()
        db_obj.status = status
        db_obj.error = error
        db_obj.updated_at = datetime.utcnow()
        await self._session.commit()
        await self._session.refresh(db_obj)
        return Task.model_validate(db_obj)
