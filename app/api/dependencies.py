# app/api/dependencies.py
from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session
from app.core.service_container import ServiceContainer
from app.domain.interfaces.task_service import ITaskService
from app.services.task_service import TaskService
from app.agents.registry import AgentRegistry
from app.agents.product_owner_agent import build_default_product_owner_agent
from app.adapters.openai_llm_adapter import OpenAILLMAdapter
from app.core.config import get_settings
from app.services.orchestrator_service import OrchestratorService
from app.services.session_service import SessionService
from app.domain.interfaces.session_service import ISessionService

_container = ServiceContainer()
_settings = get_settings()
_registry = AgentRegistry()  # global registry instance


def init_container() -> None:
    # LLM adapter
    def llm_factory() -> OpenAILLMAdapter:
        return OpenAILLMAdapter(
            api_key=_settings.openai_api_key or "",
            model=_settings.openai_model,
            base_url=_settings.openai_base_url,
        )

    # Agent registry (singleton)
    _registry.register(build_default_product_owner_agent(llm_factory()))

    # Note: DB-bound services cannot be global singleton because they need a session.
    # We'll resolve them per-request in FastAPI dependencies.


init_container()


# ---- FastAPI dependency helpers ----

async def get_task_service() -> ITaskService:
    async for session in get_session():
        yield TaskService(session)  # type: ignore[return-value]


async def get_session_service() -> ISessionService:
    async for session in get_session():
        yield SessionService(session)  # type: ignore[return-value]


def get_agent_registry() -> AgentRegistry:
    return _registry


def get_orchestrator_service(
    task_service: ITaskService,
    session_service: ISessionService,
) -> OrchestratorService:
    return OrchestratorService(
        agent_registry=_registry,
        session_service=session_service,
        task_service=task_service,
    )
