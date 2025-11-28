# app/agents/dba_agent.py
from __future__ import annotations

from textwrap import dedent

from app.agents.base_agent import BaseAgent
from app.domain.models.tasks import Task, TaskStatus
from app.domain.models.messages import Message
from app.domain.models.agents import AgentDescriptor, AgentRole


class DBAAgent(BaseAgent):
    SYSTEM_PROMPT = dedent("""
    You are a Senior Database Architect (Postgres/MySQL).
    - Analyse schemas, indexes and queries.
    - Identify missing indexes, redundant indexes, and normalization issues.
    - Recommend concrete DDL (ALTER TABLE/CREATE INDEX) where appropriate.
    - Explain trade-offs briefly.
    Output JSON: { "analysis": "...", "recommendations": ["..."], "ddl_suggestions": ["..."] }
    """)

    async def handle_task(self, task: Task, history: list[Message]) -> Task:
        task.status = TaskStatus.IN_PROGRESS
        try:
            prompt = dedent(f"""
            Task: {task.title}
            Description:
            {task.description}

            Recent conversation:
            {self._format_history(history)}

            Focus on schema/index review.
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


def build_default_dba_agent(llm: "LLMAdapter") -> DBAAgent:
    descriptor = AgentDescriptor(
        id="dba_default",
        role=AgentRole.DBA,
        display_name="DBA Agent",
        description="Performs schema/index analysis and suggests DDL changes.",
        capabilities=["schema_review", "index_suggestions"],
    )
    return DBAAgent(descriptor=descriptor, llm=llm)
