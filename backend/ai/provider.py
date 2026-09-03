import json
import os
from typing import Any

import httpx


class ProviderError(RuntimeError):
    pass


class OpenAICompatibleProvider:
    def __init__(self) -> None:
        self.api_key = os.getenv("AI_API_KEY", "").strip()
        self.base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("AI_MODEL", "gpt-5.6").strip()
        self.timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "60"))

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.model)

    async def generate_json(self, *, system: str, user: str) -> dict[str, Any]:
        if not self.available:
            raise ProviderError("AI provider is not configured")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)

        if response.status_code < 200 or response.status_code >= 300:
            raise ProviderError(f"AI provider returned HTTP {response.status_code}")

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ProviderError("AI provider returned an invalid JSON response") from exc
