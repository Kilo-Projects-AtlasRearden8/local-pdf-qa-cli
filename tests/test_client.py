"""Tests for the LLM client using a mock endpoint (no keys, no network)."""

from __future__ import annotations

import httpx
import pytest

from local_pdf_qa.client import ChatMessage, LLMClient


def _mock_client(canned: str) -> LLMClient:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": canned}}]},
        )

    transport = httpx.MockTransport(handler)
    return LLMClient(
        endpoint="http://mock/v1",
        model="test-model",
        client=httpx.Client(transport=transport),
    )


def test_chat_returns_content():
    client = _mock_client("The answer is Paris.")
    messages = [ChatMessage(role="user", content="What is the capital?")]
    answer = client.chat(messages)
    assert answer == "The answer is Paris."


def test_chat_includes_model_and_temperature():
    class CapturingTransport(httpx.MockTransport):
        def __init__(self, handler):
            super().__init__(handler)
            self.last_body = None

        def handle_request(self, request):
            self.last_body = request.read()
            return super().handle_request(request)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    cap = CapturingTransport(handler)
    client = LLMClient(
        endpoint="http://mock/v1",
        model="my-model",
        temperature=0.7,
        client=httpx.Client(transport=cap),
    )
    client.chat([ChatMessage(role="user", content="hi")])
    import json

    body = json.loads(cap.last_body)
    assert body["model"] == "my-model"
    assert body["temperature"] == 0.7
    assert body["stream"] is False
    assert body["messages"][0]["content"] == "hi"


def test_chat_raises_on_non_2xx():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, text="bad gateway")

    client = LLMClient(
        endpoint="http://mock/v1",
        model="test-model",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    with pytest.raises(httpx.HTTPStatusError):
        client.chat([ChatMessage(role="user", content="hi")])


def test_chat_raises_on_unexpected_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"not": "choices"})

    client = LLMClient(
        endpoint="http://mock/v1",
        model="test-model",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    with pytest.raises(RuntimeError):
        client.chat([ChatMessage(role="user", content="hi")])


def test_api_key_sent_when_provided():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers.get("Authorization")
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    client = LLMClient(
        endpoint="http://mock/v1",
        model="test-model",
        api_key="test-key-123",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    client.chat([ChatMessage(role="user", content="hi")])
    assert seen["authorization"] == "Bearer test-key-123"
