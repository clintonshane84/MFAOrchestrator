# app/services/session_service.py
from __future__ import annotations

import uuid
from typing import Sequence, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.interfaces.session_service import ISessionService
from app.domain.models.db_models import SessionDB, MessageDB
from app.domain.models.sessions import Session
from app.domain.models.messages import Message


class SessionService(ISessionService):
    """
    SQLModel-backed session + message service.

    Responsibilities:
    - Create and retrieve session records
    - List sessions (optionally filtered by creator)
    - Retrieve messages for a session (ordered chronologically)
    - Append messages to a session
    """

    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session

    # -------------------------
    # Session operations
    # -------------------------

    async def create_session(
        self,
        created_by: str,
        title: str | None = None,
        default_agent_id: str | None = None,
    ) -> Session:
        session_id = str(uuid.uuid4())
        db_obj = SessionDB(
            id=session_id,
            created_by=created_by,
            title=title,
            default_agent_id=default_agent_id,
        )
        self._db.add(db_obj)
        await self._db.commit()
        await self._db.refresh(db_obj)
        return Session.model_validate(db_obj)

    async def get_session(self, session_id: str) -> Session:
        stmt = select(SessionDB).where(SessionDB.id == session_id)
        result = await self._db.exec(stmt)
        db_obj = result.one()
        return Session.model_validate(db_obj)

    async def list_sessions(self, created_by: str | None = None) -> Sequence[Session]:
        stmt = select(SessionDB)
        if created_by is not None:
            stmt = stmt.where(SessionDB.created_by == created_by)

        result = await self._db.exec(stmt)
        rows = result.all()
        return [Session.model_validate(r) for r in rows]

    # -------------------------
    # Message operations
    # -------------------------

    async def get_messages(self, session_id: str) -> list[Message]:
        stmt = (
            select(MessageDB)
            .where(MessageDB.session_id == session_id)
            .order_by(MessageDB.created_at)
        )
        result = await self._db.exec(stmt)
        rows: List[MessageDB] = result.all()
        messages: list[Message] = []
        for row in rows:
            metadata = row.meta or {}
            # Ensure metadata is dict[str, str] for the domain model
            messages.append(
                Message(
                    id=row.id,
                    session_id=row.session_id,
                    agent_id=row.agent_id,
                    role=row.role,
                    content=row.content,
                    created_at=row.created_at,
                    metadata={str(k): str(v) for k, v in metadata.items()},
                )
            )
        return messages

    async def append_message(self, message: Message) -> None:
        db_obj = MessageDB(
            id=message.id,
            session_id=message.session_id,
            agent_id=message.agent_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
            metadata=message.metadata or {},
        )
        self._db.add(db_obj)
        await self._db.commit()
