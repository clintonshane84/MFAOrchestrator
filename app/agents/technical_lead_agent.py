# app/agents/technical_lead_agent.py
from __future__ import annotations

from textwrap import dedent
from typing import Any

from app.agents.base_agent import BaseAgent
from app.domain.models.tasks import Task, TaskStatus, TaskType
from app.domain.models.messages import Message
from app.domain.models.agents import AgentDescriptor, AgentRole


class TechnicalLeadAgent(BaseAgent):
    """
    Technical Lead Agent:
    - Reviews outputs from other role agents (PO, DBA, DevOps, QA).
    - Performs an internal review -> fix -> review loop within one completion.
    - Produces a structured JSON verdict, including a final improved version.
    """

    SYSTEM_PROMPT = dedent("""
    You are a Senior Technical Lead reviewing work produced by other specialist agents
    (Product Owner, DBA, DevOps, QA).

    You must:
    - Critically review the given content for correctness, clarity, completeness, and alignment with best practices.
    - Perform an internal review -> fix -> review loop as many times as needed (within reason) until you are satisfied.
    - Improve the content directly where needed.
    - Make the final output consistent, well-structured, and implementation-friendly.
    - Ensure the final result is ready to be consumed by downstream steps (e.g. ticket creation, implementation, or stakeholder review).

    Return ONLY valid JSON with the following shape:

    {
      "approved": true | false,
      "iterations": <int>,
      "original_content": "<original>",
      "final_content": "<final improved version>",
      "issues_found": ["issue 1", "issue 2", ...],
      "comments": "short narrative summary"
    }

    Notes:
    - If the original content is already excellent, 'approved' can be true and 'final_content' may be identical.
    - 'iterations' is the number of internal review passes you performed.
    """)

    async def handle_task(self, task: Task, history: list[Message]) -> Task:
        task.status = TaskStatus.IN_PROGRESS

        try:
            if task.type != TaskType.REVIEW:
                # Guardrail: TL should mainly be used for REVIEW tasks
                task.type = TaskType.REVIEW

            prompt = dedent(f"""
            You are reviewing the following artifact from another agent.

            Task title: {task.title}

            Artifact to review (content from upstream agent):
            {task.description}

            Recent session messages (most recent last):
            {self._format_history(history)}

            Remember: run an internal review -> fix -> review loop before returning.
            Output ONLY the required JSON.
            """)

            raw = await self._llm.complete(prompt, system_prompt=self.SYSTEM_PROMPT)

            # Let callers parse/validate this JSON more strictly later if desired.
            task.result = {"raw": raw}
            task.status = TaskStatus.COMPLETED
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)

        return task

    @staticmethod
    def _format_history(history: list[Message]) -> str:
        return "\n".join(f"[{m.role}] {m.content}" for m in history[-10:])


def build_default_technical_lead_agent(llm: "LLMAdapter") -> TechnicalLeadAgent:
    descriptor = AgentDescriptor(
        id="tech_lead_default",
        role=AgentRole.TECH_LEAD,
        display_name="Technical Lead Agent",
        description=(
            "Reviews and improves outputs from other agents before they are "
            "used downstream; enforces quality via review->fix->review cycles."
        ),
        capabilities=["review", "refinement", "quality_gate"],
    )
    return TechnicalLeadAgent(descriptor=descriptor, llm=llm)
