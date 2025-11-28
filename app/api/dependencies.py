# app/api/dependencies.py
from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session
from app.domain.interfaces.task_service import ITaskService
from app.domain.interfaces.session_service import ISessionService
from app.services.task_service import TaskService
from app.services.session_service import SessionService
from app.agents.registry import AgentRegistry
from app.agents.product_owner_agent import build_default_product_owner_agent
from app.agents.dba_agent import build_default_dba_agent
from app.agents.devops_agent import build_default_devops_agent
from app.agents.qa_tester_agent import build_default_qa_agent
from app.adapters.openai_llm_adapter import OpenAILLMAdapter
from app.core.config import get_settings
from app.services.orchestrator_service import OrchestratorService

_settings = get_settings()
_registry = AgentRegistry()


def _build_llm() -> OpenAILLMAdapter:
    return OpenAILLMAdapter(
        api_key=_settings.openai_api_key or "",
        model=_settings.openai_model,
        base_url=_settings.openai_base_url,
    )


def init_container() -> None:
    llm = _build_llm()
    _registry.register(build_default_product_owner_agent(llm))
    _registry.register(build_default_dba_agent(llm))
    _registry.register(build_default_devops_agent(llm))
    _registry.register(build_default_qa_agent(llm))


init_container()


# ---- FastAPI dependencies ----

async def get_task_service() -> ITaskService:
    async for db in get_session():
        yield TaskService(db)  # type: ignore[return-value]


async def get_session_service() -> ISessionService:
    async for db in get_session():
        yield SessionService(db)  # type: ignore[return-value]


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
