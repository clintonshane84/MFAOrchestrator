# app/domain/models/workflows.py
from enum import Enum
from pydantic import BaseModel
from typing import Any


class WorkflowPhase(str, Enum):
    REQUIREMENTS_QA = "requirements_qa"          # PO asks questions
    REQUIREMENTS_FINAL = "requirements_final"    # PO finalises F/NFRs
    USER_STORIES = "user_stories"                # PO generates user stories
    ARCHITECTURE = "architecture"                # ERD + class diagrams
    FILE_TREE = "file_tree"                      # BackendDev: directory layout
    CODE_SKELETON = "code_skeleton"              # BackendDev: core skeletons
    TEST_SKELETON = "test_skeleton"              # BackendDev/QA: tests
    TECH_LEAD_REVIEW = "tech_lead_review"        # TL: quality gate
    DONE = "done"


class ProjectWorkflowState(BaseModel):
    id: str
    created_by: str
    current_phase: WorkflowPhase
    artefacts: dict[str, Any]  # stores partial JSON blobs from each step
