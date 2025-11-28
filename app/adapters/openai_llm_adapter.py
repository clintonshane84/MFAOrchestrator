# app/adapters/openai_llm_adapter.py
from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.adapters.abstract_llm_adapter import LLMAdapter


class OpenAILLMAdapter(LLMAdapter):
    """
    Super-thin wrapper over OpenAI-style chat completion API.
    You can later swap this out without touching agents or orchestrator.
    """

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")

    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            return data["choices"][0]["message"]["content"]