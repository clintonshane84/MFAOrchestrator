# app/services/orchestrator_service.py
from __future__ import annotations

import uuid
from typing import Sequence

from app.agents.registry import AgentRegistry
from app.domain.models.tasks import Task, TaskStatus, TaskType
from app.domain.models.messages import Message, MessageRole
from app.domain.models.sessions import Session
from app.services.session_service import SessionService
from app.services.task_service import TaskService


class OrchestratorService:
    """
    Core brain of the platform:
    - Accepts requests from API
    - Creates sessions & tasks
    - Picks agent (or uses requested one)
    - Invokes agent.handle_task()
    - Persists history & results
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        session_service: SessionService,
        task_service: TaskService,
    ) -> None:
        self._agents = agent_registry
        self._sessions = session_service
        self._tasks = task_service

    async def start_session(
        self,
        created_by: str,
        title: str | None = None,
        default_agent_id: str | None = None,
    ) -> Session:
        session = await self._sessions.create_session(
            created_by=created_by,
            title=title,
            default_agent_id=default_agent_id,
        )
        return session

    async def submit_task(
        self,
        session_id: str,
        agent_id: str,
        title: str,
        description: str,
        task_type: TaskType = TaskType.ANALYSIS,
    ) -> Task:
        session = await self._sessions.get_session(session_id)
        _ = session  # ensure it exists

        task = await self._tasks.create_task(
            session_id=session_id,
            agent_id=agent_id,
            title=title,
            description=description,
            task_type=task_type,
        )

        agent = self._agents.get(agent_id)
        history: list[Message] = await self._sessions.get_messages(session_id)

        # Log a user message representing the request
        request_message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            agent_id=None,
            role=MessageRole.USER,
            content=description,
        )
        await self._sessions.append_message(request_message)

        task = await agent.handle_task(task, history + [request_message])

        # Persist updated task + agent response
        await self._tasks.update_task(task)

        if task.result is not None:
            response_message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                agent_id=agent_id,
                role=MessageRole.ASSISTANT,
                content=str(task.result),
            )
            await self._sessions.append_message(response_message)

        return task