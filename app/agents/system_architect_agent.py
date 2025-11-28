# app/agents/system_architect_agent.py
from __future__ import annotations

from textwrap import dedent
from typing import Any

from app.agents.base_agent import BaseAgent
from app.domain.models.tasks import Task, TaskStatus
from app.domain.models.messages import Message
from app.domain.models.agents import AgentDescriptor, AgentRole


class SystemArchitectAgent(BaseAgent):
    """
    Responsible for:
    - Translating user stories + F/NFRs into an ERD (mermaid)
    - Drafting a class diagram (mermaid) for core domain objects
    """

    SYSTEM_PROMPT = dedent("""
    You are a Senior System Architect.

    Given user stories and functional/non-functional requirements:
    - Design the core domain entities and relationships.
    - Express the data model as a concise ERD using Mermaid `erDiagram` syntax.
    - Express the object model as a Mermaid `classDiagram`, focusing on core classes
      (entities, value objects, services) and key methods/attributes.

    Output STRICT JSON:

    {
      "erd_mermaid": "```mermaid\\nerDiagram\\n ...```",
      "class_diagram_mermaid": "```mermaid\\nclassDiagram\\n ...```",
      "notes": "short explanation of key design choices"
    }

    Rules:
    - Keep diagrams readable and not overly detailed.
    - Only include the most important entities/classes for a first iteration.
    - Use snake_case or lowerCamelCase for attributes; avoid framework-specific details.
    """)

    async def handle_task(self, task: Task, history: list[Message]) -> Task:
        task.status = TaskStatus.IN_PROGRESS

        try:
            prompt = dedent(f"""
            You are designing architecture from this context.

            Task title: {task.title}

            Input bundle (user stories + requirements):
            {task.description}

            Recent conversation (most recent last):
            {self._format_history(history)}

            Produce the JSON as specified.
            """)

            raw = await self._llm.complete(prompt, system_prompt=self.SYSTEM_PROMPT)

            task.result = {"raw": raw}
            task.status = TaskStatus.COMPLETED
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)

        return task

    @staticmethod
    def _format_history(history: list[Message]) -> str:
        return "\n".join(f"[{m.role}] {m.content}" for m in history[-10:])


def build_default_system_architect_agent(llm: "LLMAdapter") -> SystemArchitectAgent:
    descriptor = AgentDescriptor(
        id="system_architect_default",
        role=AgentRole.SYSTEM_ARCHITECT,
        display_name="System Architect Agent",
        description="Generates ERD and class diagrams from user stories and requirements.",
        capabilities=["erd_design", "class_diagram_design"],
    )
    return SystemArchitectAgent(descriptor=descriptor, llm=llm)
