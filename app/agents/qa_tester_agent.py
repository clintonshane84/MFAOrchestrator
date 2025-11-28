# app/agents/qa_tester_agent.py
from __future__ import annotations

from textwrap import dedent

from app.agents.base_agent import BaseAgent
from app.domain.models.tasks import Task, TaskStatus
from app.domain.models.messages import Message
from app.domain.models.agents import AgentDescriptor, AgentRole


class QATesterAgent(BaseAgent):
    SYSTEM_PROMPT = dedent("""
    You are a Senior QA/Test Engineer.
    - Design test cases and regression suites.
    - Highlight edge cases and non-functional concerns.
    Output JSON: { "test_cases": [...], "edge_cases": [...], "regression_suite": [...], "notes": "..." }
    """)

    async def handle_task(self, task: Task, history: list[Message]) -> Task:
        task.status = TaskStatus.IN_PROGRESS
        try:
            prompt = dedent(f"""
            Feature/Change: {task.title}
            Details:
            {task.description}

            Recent conversation:
            {self._format_history(history)}
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


def build_default_qa_agent(llm: "LLMAdapter") -> QATesterAgent:
    descriptor = AgentDescriptor(
        id="qa_default",
        role=AgentRole.QA_TESTER,
        display_name="QA Tester Agent",
        description="Generates test cases and regression suites.",
        capabilities=["test_case_design", "regression_planning"],
    )
    return QATesterAgent(descriptor=descriptor, llm=llm)
