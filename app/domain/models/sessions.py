# app/domain/models/sessions.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Session(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    title: str | None = None
    default_agent_id: str | None = None
