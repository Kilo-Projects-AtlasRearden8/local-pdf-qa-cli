"""Application configuration for local-pdf-qa-cli."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_ENDPOINT = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3"
DEFAULT_SESSION_FILE = "qa_sessions.json"
DEFAULT_TEMPERATURE = 0.3


@dataclass
class AppConfig:
    endpoint: str
    model: str
    session_file: str
    temperature: float
    api_key: str | None = None

    @property
    def chat_url(self) -> str:
        return self.endpoint.rstrip("/") + "/chat/completions"


def load_config(
    *,
    endpoint: str | None = None,
    model: str | None = None,
    session_file: str | None = None,
    temperature: float | None = None,
    api_key: str | None = None,
) -> AppConfig:
    """Build configuration from arguments, environment variables, and defaults.

    Command-line arguments win, then environment variables, then built-in
    defaults. No API key is required by default (Ollama needs none).
    """
    return AppConfig(
        endpoint=endpoint or os.environ.get("LOCAL_PDF_QA_ENDPOINT") or DEFAULT_ENDPOINT,
        model=model or os.environ.get("LOCAL_PDF_QA_MODEL") or DEFAULT_MODEL,
        session_file=session_file or DEFAULT_SESSION_FILE,
        temperature=(DEFAULT_TEMPERATURE if temperature is None else float(temperature)),
        api_key=api_key or os.environ.get("LOCAL_PDF_QA_API_KEY"),
    )
