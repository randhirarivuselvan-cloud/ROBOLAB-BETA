from __future__ import annotations

import json
import os
from typing import Any

import httpx


class ProviderError(RuntimeError):
    pass


class OpenAICompatibleProvider:
    """Small OpenAI-compatible transport shared by the 48 specialist roles."""

    def __init__(self) -> None:
        self.api_key = os.getenv("AI_API_KEY", "").strip()
        self.base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("AI_MODEL", "gpt-5.6").strip()
        self.timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "60"))
        self.max_retries = max(0, int(os.getenv("AI_MAX_RETRIES", "2")))

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.model)

    async def generate_json(
        self,
        *,
        system: str,
        user: str,
        model: str | None = None,
        temperature: float = 0.15,
    ) -> dict[str, Any]:
        if not self.available:
            raise ProviderError("AI provider is not configured")

        payload = {
            "model": (model or self.model).strip() or self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers=headers,
                    )
                if 200 <= response.status_code < 300:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content)
                last_error = ProviderError(f"AI provider returned HTTP {response.status_code}")
            except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
                last_error = exc
            if attempt < self.max_retries:
                continue

        if isinstance(last_error, ProviderError):
            raise last_error
        raise ProviderError("AI provider returned an invalid or unreachable response") from last_error
