"""Tests for question answering over local PDF text."""

from __future__ import annotations

from local_pdf_qa.client import LLMClient
from local_pdf_qa.qa import answer_question


class FakeClient(LLMClient):
    """Client that returns a canned answer without touching the network."""

    def __init__(self, answer: str, check_content: bool = True) -> None:
        self.answer = answer
        self.endpoint = "http://mock/v1"
        self.model = "fake-model"
        self.calls = 0
        self.check_content = check_content

    def chat(self, messages):
        self.calls += 1
        if self.check_content:
            # Confirm the document text made it into the prompt.
            assert any("Project Alpha budget" in m.content for m in messages)
        return self.answer


def test_answer_question_uses_local_pdf_text(sample_pdf, tmp_path):
    client = FakeClient("The budget is one thousand dollars.")
    answer = answer_question(
        client=client, pdf_path=str(sample_pdf), question="What is the budget?"
    )
    assert answer == "The budget is one thousand dollars."
    assert client.calls == 1


def test_answer_question_truncates_long_text(sample_pdf):
    client = FakeClient("ok", check_content=False)
    answer_question(
        client=client,
        pdf_path=str(sample_pdf),
        question="q",
        max_chars=5,
    )
    assert client.calls == 1
