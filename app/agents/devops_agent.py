# app/agents/devops_agent.py
from __future__ import annotations

from textwrap import dedent

from app.agents.base_agent import BaseAgent
from app.domain.models.tasks import Task, TaskStatus
from app.domain.models.messages import Message
from app.domain.models.agents import AgentDescriptor, AgentRole


class DevOpsAgent(BaseAgent):
    SYSTEM_PROMPT = dedent("""
    You are a Senior SRE/DevOps engineer.
    - Diagnose incidents from logs and metrics descriptions.
    - Suggest runbook-style steps and mitigations.
    - Propose observability improvements (alerts, dashboards).
    Output JSON: { "incident_summary": "...", "likely_causes": ["..."], "mitigation_steps": ["..."], "follow_up_tasks": ["..."] }
    """)

    async def handle_task(self, task: Task, history: list[Message]) -> Task:
        task.status = TaskStatus.IN_PROGRESS
        try:
            prompt = dedent(f"""
            Incident/Task: {task.title}
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


def build_default_devops_agent(llm: "LLMAdapter") -> DevOpsAgent:
    descriptor = AgentDescriptor(
        id="devops_default",
        role=AgentRole.DEVOPS,
        display_name="DevOps Agent",
        description="Provides incident diagnostics and runbook-style responses.",
        capabilities=["incident_analysis", "runbook_suggestions"],
    )
    return DevOpsAgent(descriptor=descriptor, llm=llm)
