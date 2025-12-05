# app/core/config.py
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Multi-Agent Workforce"
    env: str = "dev"

    database_url: str = Field(
        default="postgresql+psycopg://agent:agent@localhost:5432/agentdb",
        description="SQLAlchemy-style URL for Postgres.",
    )

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
