# app/main.py
from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import agents, sessions, tasks, human_review
from app.core.logging import configure_logging
from app.core.db import init_db
from app.api.dependencies import init_container


def create_app() -> FastAPI:
    """
    Application factory for the multi-agent workforce API.
    Sets up logging, DI wiring, DB, and routes.
    """
    configure_logging()
    init_container()

    app = FastAPI(
        title="Multi-Agent Workforce API",
        version="0.1.0",
    )

    # Routers
    app.include_router(agents.router, prefix="/agents", tags=["agents"])
    app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    app.include_router(human_review.router, prefix="/human-review", tags=["human-review"])

    @app.on_event("startup")
    async def on_startup() -> None:  # noqa: D401
        """
        Application startup hook.
        - Initialize DB schema
        """
        await init_db()

    return app


app = create_app()
