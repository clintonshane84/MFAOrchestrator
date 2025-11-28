# app/agents/registry.py
from __future__ import annotations

from typing import Dict

from app.domain.models.agents import AgentDescriptor, AgentRole
from app.agents.base_agent import BaseAgent


class AgentRegistry:
    """
    Keeps a registry of live agent instances keyed by ID.
    This provides a clean seam to plug in/remove agents.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.descriptor.id] = agent

    def get(self, agent_id: str) -> BaseAgent:
        try:
            return self._agents[agent_id]
        except KeyError:
            raise KeyError(f"Agent '{agent_id}' not registered")

    def list_descriptors(self) -> list[AgentDescriptor]:
        return [agent.descriptor for agent in self._agents.values()]

    def find_by_role(self, role: AgentRole) -> list[AgentDescriptor]:
        return [
            agent.descriptor
            for agent in self._agents.values()
            if agent.descriptor.role == role
        ]