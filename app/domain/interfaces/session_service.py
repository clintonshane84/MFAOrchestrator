# app/domain/interfaces/session_service.py
from __future__ import annotations

from typing import Protocol, Sequence

from app.domain.models.sessions import Session
from app.domain.models.messages import Message


class ISessionService(Protocol):
    async def create_session(
        self,
        created_by: str,
        title: str | None = None,
        default_agent_id: str | None = None,
    ) -> Session: ...

    async def get_session(self, session_id: str) -> Session: ...

    async def list_sessions(self, created_by: str | None = None) -> Sequence[Session]: ...

    async def get_messages(self, session_id: str) -> list[Message]: ...

    async def append_message(self, message: Message) -> None: ...
