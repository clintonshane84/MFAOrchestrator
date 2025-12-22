# app/domain/models/db_models.py
from __future__ import annotations

from datetime import datetime

from sqlmodel import SQLModel, Field, Column, JSON

from app.domain.models.tasks import TaskPriority, TaskStatus, TaskType
from app.domain.models.messages import MessageRole
from app.domain.models.agents import AgentRole


class SessionDB(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    title: str | None = None
    default_agent_id: str | None = Field(default=None, index=True)


class TaskDB(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(primary_key=True, index=True)
    session_id: str = Field(foreign_key="sessions.id", index=True)
    agent_id: str = Field(index=True)

    type: TaskType
    title: str
    description: str

    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    result: dict | None = Field(sa_column=Column(JSON, nullable=True))
    error: str | None = None


class MessageDB(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(primary_key=True, index=True)
    session_id: str = Field(foreign_key="sessions.id", index=True)
    agent_id: str | None = Field(default=None, index=True)

    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta: dict | None = Field(sa_column=Column(JSON, nullable=True), default=None)


class AgentDescriptorDB(SQLModel, table=True):
    __tablename__ = "agents"

    id: str = Field(primary_key=True)
    role: AgentRole = Field(index=True)
    display_name: str
    description: str
    capabilities: list[str] = Field(
        sa_column=Column(JSON, nullable=False, default=list)
    )
