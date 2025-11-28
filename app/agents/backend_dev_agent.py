# app/agents/backend_dev_agent.py
from __future__ import annotations

from textwrap import dedent
from typing import Any

from app.agents.base_agent import BaseAgent
from app.domain.models.tasks import Task, TaskStatus, TaskType
from app.domain.models.messages import Message
from app.domain.models.agents import AgentDescriptor, AgentRole


class BackendDevAgent(BaseAgent):
    """
    Responsible for:
    - Proposing file/directory structure
    - Generating initial code skeletons for the project
    - Optionally generating unit test skeletons
    """

    SYSTEM_PROMPT_SKELETON = dedent("""
    You are a Senior Backend Engineer.

    Given:
    - User stories
    - ERD (Mermaid)
    - Class diagram (Mermaid)
    - Target stack: Python, FastAPI backend

    Your tasks:
    1) Propose a file/directory tree for the backend following clean architecture.
    2) Generate code skeletons (not full implementations) for key modules:
       - Domain models
       - Repositories / persistence layer
       - Services / use cases
       - API routes
    3) Ensure code is PEP-8 and type-annotated.
    4) Do NOT include external secrets or environment values.

    Output STRICT JSON:

    {
      "file_tree": "project_root/\\n  app/\\n    ...",
      "code_skeletons": [
        {
          "path": "app/domain/models/user.py",
          "language": "python",
          "content": "from __future__ import annotations\\n..."
        },
        ...
      ],
      "notes": "short explanation"
    }
    """)

    SYSTEM_PROMPT_TESTS = dedent("""
    You are a Senior Backend Engineer writing unit test skeletons.

    Given:
    - File tree
    - Code skeletons (core modules)

    Your tasks:
    - Propose pytest-based unit tests for critical services/routes.
    - Focus on test structure, naming, and arranging code for future implementation.
    - Do NOT assume access to a real DB; use mocks or in-memory doubles.

    Output STRICT JSON:

    {
      "test_skeletons": [
        {
          "path": "app/tests/unit/test_service_x.py",
          "language": "python",
          "content": "import pytest\\n..."
        },
        ...
      ],
      "notes": "short explanation"
    }
    """)

    async def handle_task(self, task: Task, history: list[Message]) -> Task:
        task.status = TaskStatus.IN_PROGRESS

        try:
            if task.type == TaskType.CODE_SKELETON:
                raw = await self._handle_code_skeleton(task, history)
            elif task.type == TaskType.TEST_GENERATION:
                raw = await self._handle_test_generation(task, history)
            else:
                # Default: treat as code skeleton
                raw = await self._handle_code_skeleton(task, history)

            task.result = {"raw": raw}
            task.status = TaskStatus.COMPLETED
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)

        return task

    async def _handle_code_skeleton(
        self,
        task: Task,
        history: list[Message],
    ) -> str:
        prompt = dedent(f"""
        You are generating a backend skeleton.

        Input bundle (user stories + ERD + class diagram):
        {task.description}

        Recent conversation:
        {self._format_history(history)}

        Produce JSON as specified.
        """)
        return await self._llm.complete(
            prompt,
            system_prompt=self.SYSTEM_PROMPT_SKELETON,
        )

    async def _handle_test_generation(
        self,
        task: Task,
        history: list[Message],
    ) -> str:
        prompt = dedent(f"""
        You are generating pytest test skeletons.

        Input bundle (existing file tree + code skeletons):
        {task.description}

        Recent conversation:
        {self._format_history(history)}

        Produce JSON as specified.
        """)
        return await self._llm.complete(
            prompt,
            system_prompt=self.SYSTEM_PROMPT_TESTS,
        )

    @staticmethod
    def _format_history(history: list[Message]) -> str:
        return "\n".join(f"[{m.role}] {m.content}" for m in history[-10:])


def build_default_backend_dev_agent(llm: "LLMAdapter") -> BackendDevAgent:
    descriptor = AgentDescriptor(
        id="backend_dev_default",
        role=AgentRole.BACKEND_DEV,
        display_name="Backend Developer Agent",
        description="Generates backend file layout, code skeletons, and test skeletons.",
        capabilities=[
            "file_tree_design",
            "code_skeleton_generation",
            "test_skeleton_generation",
        ],
    )
    return BackendDevAgent(descriptor=descriptor, llm=llm)
