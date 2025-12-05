# app/api/routes/workflows.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.domain.models.workflow import ProjectScaffoldResult
from app.services.orchestrator_service import OrchestratorService
from app.services.project_workflow_service import ProjectWorkflowService
from app.api.dependencies import get_orchestrator_service

router = APIRouter()


class ProjectScaffoldRequest(BaseModel):
    created_by: str
    initial_requirements: str


@router.post("/scaffold", response_model=ProjectScaffoldResult)
async def run_project_scaffold(
    body: ProjectScaffoldRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
):
    svc = ProjectWorkflowService(orchestrator)
    result = await svc.run_full_scaffold(
        created_by=body.created_by,
        initial_requirements=body.initial_requirements,
    )
    return result
