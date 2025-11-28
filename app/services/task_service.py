# app/services/task_service.py
from __future__ import annotations

import uuid
from datetime import datetime

from app.domain.models.tasks import Task, TaskType, TaskStatus


class TaskService:
    """
    Persistence boundary for tasks.
    Replace internal storage with SQLModel/SQLAlchemy later.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    async def create_task(
        self,
        session_id: str,
        agent_id: str,
        title: str,
        description: str,
        task_type: TaskType,
    ) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            session_id=session_id,
            agent_id=agent_id,
            type=task_type,
            title=title,
            description=description,
        )
        self._tasks[task_id] = task
        return task

    async def update_task(self, task: Task) -> Task:
        task.updated_at = datetime.utcnow()
        self._tasks[task.id] = task
        return task

    async def get_task(self, task_id: str) -> Task:
        return self._tasks[task_id]