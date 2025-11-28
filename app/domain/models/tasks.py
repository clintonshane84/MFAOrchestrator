# app/domain/models/tasks.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    ANALYSIS = "analysis"
    TICKET_CREATION = "ticket_creation"
    INVESTIGATION = "investigation"
    DESIGN = "design"
    OTHER = "other"
    REVIEW = "review"
    REQUIREMENTS_GATHERING = "requirements_gathering"
    CODE_SKELETON = "code_skeleton"
    TEST_GENERATION = "test_generation"


class Task(BaseModel):
    """
    Domain-level Task model used in services and API.
    Backed by TaskDB via SQLModel; validated with from_attributes=True.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    agent_id: str
    type: TaskType
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    result: dict[str, Any] | None = None
    error: str | None = None
