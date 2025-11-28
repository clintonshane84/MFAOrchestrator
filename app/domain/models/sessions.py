# app/domain/models/sessions.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.models.agents import AgentRole


class Session(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    default_agent_role: AgentRole | None = None
    title: str | None = None