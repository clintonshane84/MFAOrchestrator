# app/domain/models/workflow.py
from __future__ import annotations

from pydantic import BaseModel
from typing import Any


class ProjectScaffoldResult(BaseModel):
    requirements_raw: dict[str, Any]
    user_stories_raw: dict[str, Any]
    architecture_raw: dict[str, Any]
    code_skeleton_raw: dict[str, Any]
    tech_lead_review_raw: dict[str, Any]
