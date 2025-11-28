# app/api/routes/tasks.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.domain.models.tasks import TaskType
from app.services.orchestrator_service import OrchestratorService
from app.api.dependencies import get_orchestrator_service

router = APIRouter()


class TaskCreateRequest(BaseModel):
    session_id: str
    agent_id: str
    title: str
    description: str
    type: TaskType = TaskType.ANALYSIS


@router.post("/", summary="Submit a new task to a specific agent")
async def submit_task(
    body: TaskCreateRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
):
    task = await orchestrator.submit_task(
        session_id=body.session_id,
        agent_id=body.agent_id,
        title=body.title,
        description=body.description,
        task_type=body.type,
    )
    return task
