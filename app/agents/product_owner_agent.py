# app/agents/product_owner_agent.py
from __future__ import annotations

from textwrap import dedent

from app.agents.base_agent import BaseAgent
from app.domain.models.tasks import Task, TaskStatus, TaskType
from app.domain.models.messages import Message
from app.domain.models.agents import AgentDescriptor, AgentRole


class ProductOwnerAgent(BaseAgent):
    """
    Agent specialised in:
    - turning problem statements into user stories
    - refining acceptance criteria
    - suggesting backlog ordering
    """

    SYSTEM_PROMPT = dedent("""
    You are a Senior Product Owner.
    - Produce clear, INVEST user stories.
    - Include 'As a', 'I want', 'So that' format.
    - Provide numbered acceptance criteria.
    - Keep language concise and implementation-free.
    Output JSON with fields: user_stories, notes.
    """)

    async def handle_task(self, task: Task, history: list[Message]) -> Task:
        task.status = TaskStatus.IN_PROGRESS

        try:
            prompt = dedent(f"""
            Context:
            Task type: {task.type}
            Title: {task.title}
            Description:
            {task.description}

            Conversation history (most recent last):
            {self._format_history(history)}

            Produce JSON only.
            """)
            raw = await self._llm.complete(prompt, system_prompt=self.SYSTEM_PROMPT)

            # For now, trust JSON; later we add robust JSON parsing & validation.
            task.result = {"raw": raw}
            task.status = TaskStatus.COMPLETED
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)

        return task

    @staticmethod
    def _format_history(history: list[Message]) -> str:
        lines: list[str] = []
        for msg in history[-10:]:
            lines.append(f"[{msg.role}] {msg.content}")
        return "\n".join(lines)


def build_default_product_owner_agent(llm: "LLMAdapter") -> ProductOwnerAgent:
    descriptor = AgentDescriptor(
        id="product_owner_default",
        role=AgentRole.PRODUCT_OWNER,
        display_name="Product Owner Agent",
        description="Transforms problem descriptions into user stories and acceptance criteria.",
        capabilities=["user_story_generation", "acceptance_criteria", "backlog_refinement"],
    )
    return ProductOwnerAgent(descriptor=descriptor, llm=llm)