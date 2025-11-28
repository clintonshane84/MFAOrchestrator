# app/api/main.py
from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import agents, sessions, tasks
from app.core.config import settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Multi-Agent Workforce API", version="0.1.0")

    app.include_router(agents.router, prefix="/agents", tags=["agents"])
    app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

    return app


app = create_app()