# app/domain/models/agents.py
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class AgentRole(str, Enum):
    PRODUCT_OWNER = "product_owner"
    DBA = "dba"
    DEVOPS = "devops"
    QA_TESTER = "qa_tester"


class AgentDescriptor(BaseModel):
    id: str
    role: AgentRole
    display_name: str
    description: str
    capabilities: list[str]