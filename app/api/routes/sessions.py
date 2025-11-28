# app/api/routes/sessions.py
from __future__ import annotations

from fastapi import APIRouter

from pydantic import BaseModel

from app.services.orchestrator_service import OrchestratorService
from app.dependencies import get_orchestrator_service  # typical DI pattern

router = APIRouter()


class SessionCreateRequest(BaseModel):
    created_by: str
    title: str | None = None
    default_agent_id: str | None = None


@router.post("/", summary="Create a new agent session")
async def create_session(
    body: SessionCreateRequest,
    orchestrator: OrchestratorService = get_orchestrator_service(),
):
    session = await orchestrator.start_session(
        created_by=body.created_by,
        title=body.title,
        default_agent_id=body.default_agent_id,
    )
    return session