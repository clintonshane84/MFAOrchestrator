# app/agents/base_agent.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, Any

from app.domain.models.tasks import Task
from app.domain.models.messages import Message
from app.domain.models.agents import AgentDescriptor


class LLMAdapter(Protocol):
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str: ...


class BaseAgent(ABC):
    """
    Base class for all role-specific agents.
    Implements common flow; subclasses specialise prompts & post-processing.
    """

    def __init__(self, descriptor: AgentDescriptor, llm: LLMAdapter) -> None:
        self._descriptor = descriptor
        self._llm = llm

    @property
    def descriptor(self) -> AgentDescriptor:
        return self._descriptor

    @abstractmethod
    async def handle_task(self, task: Task, history: list[Message]) -> Task:
        """
        Main entry point called by OrchestratorService.
        Should not raise unhandled exceptions; encode them into Task.error.
        """
        raise NotImplementedError