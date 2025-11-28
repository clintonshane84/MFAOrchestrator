# app/api/routes/agents.py
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.agents.registry import AgentRegistry
from app.api.dependencies import get_agent_registry

router = APIRouter()


@router.get("/", summary="List available agents")
async def list_agents(
    registry: AgentRegistry = Depends(get_agent_registry),
):
    return registry.list_descriptors()
