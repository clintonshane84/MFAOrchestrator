# app/core/llm_policy.py
from app.domain.models.workflows import WorkflowPhase

def model_for_phase(phase: WorkflowPhase) -> str:
    if phase == WorkflowPhase.REQUIREMENTS_QA:
        return "gpt-5-nano"
    if phase in {
        WorkflowPhase.REQUIREMENTS_FINAL,
        WorkflowPhase.USER_STORIES,
        WorkflowPhase.ARCHITECTURE,
        WorkflowPhase.FILE_TREE,
        WorkflowPhase.CODE_SKELETON,
        WorkflowPhase.TEST_SKELETON,
        WorkflowPhase.TECH_LEAD_REVIEW,
    }:
        return "gpt-5-mini"
    return "gpt-5-mini"
