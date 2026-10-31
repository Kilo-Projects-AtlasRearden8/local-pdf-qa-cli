"""Question answering over local PDF text via an LLM endpoint."""

from __future__ import annotations

from .client import ChatMessage, LLMClient
from .extract import extract_text

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about a PDF document. "
    "Answer only using the provided document text. If the answer is not in the "
    "document, say so. Do not make up facts. Keep answers concise and plain."
)


def build_prompt(pdf_text: str, question: str) -> list[ChatMessage]:
    """Build the system/user messages sent to the endpoint."""
    return [
        ChatMessage(role="system", content=SYSTEM_PROMPT),
        ChatMessage(
            role="user",
            content=(f"Document text:\n---\n{pdf_text}\n---\n\nQuestion: {question}\nAnswer:"),
        ),
    ]


def answer_question(
    *,
    client: LLMClient,
    pdf_path: str,
    question: str,
    max_chars: int = 12000,
) -> str:
    """Extract text from a local PDF and ask the LLM to answer a question about it.

    The PDF is read locally; nothing is uploaded.
    """
    pdf_text = extract_text(pdf_path)
    if len(pdf_text) > max_chars:
        pdf_text = pdf_text[:max_chars]
    messages = build_prompt(pdf_text, question)
    return client.chat(messages)
