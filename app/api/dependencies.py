# app/api/dependencies.py
from __future__ import annotations

from fastapi import Depends

from app.core.config import get_settings
from app.core.db import get_session
from app.agents.registry import AgentRegistry
from app.agents.product_owner_agent import build_default_product_owner_agent
from app.agents.dba_agent import build_default_dba_agent
from app.agents.devops_agent import build_default_devops_agent
from app.agents.qa_tester_agent import build_default_qa_agent
from app.adapters.openai_llm_adapter import OpenAILLMAdapter
from app.domain.interfaces.task_service import ITaskService
from app.domain.interfaces.session_service import ISessionService
from app.services.task_service import TaskService
from app.services.session_service import SessionService
from app.services.orchestrator_service import OrchestratorService
from app.agents.system_architect_agent import build_default_system_architect_agent
from app.agents.backend_dev_agent import build_default_backend_dev_agent

_settings = get_settings()
_registry = AgentRegistry()
_initialized: bool = False


def _build_llm() -> OpenAILLMAdapter:
    return OpenAILLMAdapter(
        api_key=_settings.openai_api_key or "",
        model=_settings.openai_model,
        base_url=_settings.openai_base_url,
    )


def init_container() -> None:
    """
    Register all built-in agents with the global registry.
    Idempotent: safe to call multiple times.
    """
    global _initialized
    if _initialized:
        return

    llm = _build_llm()

    _registry.register(build_default_product_owner_agent(llm))
    _registry.register(build_default_dba_agent(llm))
    _registry.register(build_default_devops_agent(llm))
    _registry.register(build_default_qa_agent(llm))
    _registry.register(build_default_technical_lead_agent(llm))
    _registry.register(build_default_system_architect_agent(llm))   # NEW
    _registry.register(build_default_backend_dev_agent(llm))

    _initialized = True


# ---- Service dependencies ----


async def get_task_service() -> ITaskService:
    """
    Resolve a TaskService bound to an AsyncSession.
    """
    async for db_session in get_session():
        # FastAPI will handle the async generator as a dependency
        yield TaskService(db_session)  # type: ignore[return-value]


async def get_session_service() -> ISessionService:
    """
    Resolve a SessionService bound to an AsyncSession.
    """
    async for db_session in get_session():
        yield SessionService(db_session)  # type: ignore[return-value]


def get_agent_registry() -> AgentRegistry:
    """
    Resolve the global AgentRegistry instance.
    """
    return _registry


def get_orchestrator_service(
    task_service: ITaskService = Depends(get_task_service),
    session_service: ISessionService = Depends(get_session_service),
    agent_registry: AgentRegistry = Depends(get_agent_registry),
) -> OrchestratorService:
    """
    Resolve an OrchestratorService for the current request.
    It is cheap and stateless, so we build a new one per request.
    """
    return OrchestratorService(
        agent_registry=agent_registry,
        session_service=session_service,
        task_service=task_service,
    )
