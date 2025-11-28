# app/services/session_service.py
from __future__ import annotations

import uuid
from typing import Dict, List

from app.domain.models.sessions import Session
from app.domain.models.messages import Message


class SessionService:
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}
        self._messages_by_session: Dict[str, List[Message]] = {}

    async def create_session(
        self,
        created_by: str,
        title: str | None = None,
        default_agent_id: str | None = None,
    ) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            created_by=created_by,
            title=title,
        )
        self._sessions[session_id] = session
        self._messages_by_session[session_id] = []
        return session

    async def get_session(self, session_id: str) -> Session:
        return self._sessions[session_id]

    async def get_messages(self, session_id: str) -> list[Message]:
        return list(self._messages_by_session.get(session_id, []))

    async def append_message(self, message: Message) -> None:
        self._messages_by_session.setdefault(message.session_id, []).append(message)