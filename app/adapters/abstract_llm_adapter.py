# app/adapters/abstract_llm_adapter.py
from __future__ import annotations

from typing import Protocol


class LLMAdapter(Protocol):
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str: ...