"""OpenAI-compatible HTTP client (default Ollama). No API key required by default."""

from __future__ import annotations

from collections.abc import Iterable

import httpx


class ChatMessage:
    """A single message sent to the chat endpoint."""

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class LLMClient:
    """Talks to an OpenAI-compatible ``/chat/completions`` endpoint.

    Defaults to Ollama (``http://localhost:11434/v1``), which needs no API key.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        model: str,
        temperature: float = 0.3,
        api_key: str | None = None,
        timeout: float = 60.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        self.timeout = timeout
        # Injected client (used in tests with a mock transport). When None a
        # temporary client is created per request.
        self._client = client

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(self, messages: Iterable[ChatMessage]) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self.temperature,
            "stream": False,
        }

        def post(client: httpx.Client) -> httpx.Response:
            return client.post(
                f"{self.endpoint}/chat/completions",
                headers=self._headers(),
                json=payload,
            )

        if self._client is not None:
            response = post(self._client)
        else:
            with httpx.Client(timeout=self.timeout) as client:
                response = post(client)

        response.raise_for_status()
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected endpoint response: {data!r}") from exc
