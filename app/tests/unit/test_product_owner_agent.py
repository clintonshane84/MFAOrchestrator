# app/tests/unit/test_product_owner_agent.py
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.agents.product_owner_agent import build_default_product_owner_agent
from app.domain.models.tasks import Task, TaskType
from app.domain.models.messages import Message, MessageRole


class DummyLLM:
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        return '{"user_stories": [], "notes": "stubbed"}'


@pytest.mark.asyncio
async def test_product_owner_agent_handles_basic_task() -> None:
    agent = build_default_product_owner_agent(llm=DummyLLM())  # type: ignore[arg-type]

    task = Task(
        id="task-1",
        session_id="sess-1",
        agent_id=agent.descriptor.id,
        type=TaskType.ANALYSIS,
        title="Test story",
        description="We need a new login flow.",
    )

    history: list[Message] = [
        Message(
            id="m1",
            session_id="sess-1",
            agent_id=None,
            role=MessageRole.USER,
            content="Please generate user stories.",
        )
    ]

    result_task = await agent.handle_task(task, history)

    assert result_task.status.name == "COMPLETED"
    assert result_task.result is not None