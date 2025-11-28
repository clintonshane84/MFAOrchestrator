# app/api/routes/human_review.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.orchestrator_service import OrchestratorService
from app.api.dependencies import get_orchestrator_service

router = APIRouter()


class HumanApprovalRequest(BaseModel):
    note: str | None = None


class HumanRejectRequest(BaseModel):
    reason: str


@router.post("/{task_id}/request", summary="Mark task as waiting for human input")
async def request_human(
    task_id: str,
    body: HumanApprovalRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
):
    return await orchestrator.request_human_approval(task_id, body.note)


@router.post("/{task_id}/approve", summary="Approve a waiting task")
async def approve_task(
    task_id: str,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
):
    return await orchestrator.approve_task(task_id)


@router.post("/{task_id}/reject", summary="Reject a waiting task")
async def reject_task(
    task_id: str,
    body: HumanRejectRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
):
    return await orchestrator.reject_task(task_id, body.reason)
