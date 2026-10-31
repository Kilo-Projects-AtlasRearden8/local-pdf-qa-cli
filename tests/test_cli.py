"""Tests for the CLI using a fake client (no keys, no network)."""

from __future__ import annotations

import json

import pytest

from local_pdf_qa import cli


class FakeClient:
    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.endpoint = "http://mock/v1"
        self.model = "fake-model"
        self.calls = 0

    def chat(self, messages):
        self.calls += 1
        assert any("Project Alpha budget" in m.content for m in messages)
        return self.answer


def _monkeypatch_client(monkeypatch: pytest.MonkeyPatch, answer: str) -> FakeClient:
    client = FakeClient(answer)

    def fake_client_from_args(args):
        return client

    monkeypatch.setattr(cli, "_client_from_args", fake_client_from_args)
    return client


def _global_flags(session_file):
    return ["--session-file", str(session_file), "--endpoint", "http://mock/v1"]


def test_ask_prints_answer_and_saves_session(
    monkeypatch: pytest.MonkeyPatch,
    sample_pdf,
    tmp_session_file,
):
    client = _monkeypatch_client(monkeypatch, "The budget is one thousand dollars.")
    exit_code = cli.main(
        _global_flags(tmp_session_file)
        + [
            "--model",
            "fake-model",
            "ask",
            str(sample_pdf),
            "What is the budget?",
        ]
    )
    assert exit_code == 0
    assert client.calls == 1
    data = json.loads(tmp_session_file.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["question"] == "What is the budget?"
    assert data[0]["answer"] == "The budget is one thousand dollars."
    assert data[0]["pdf"] == str(sample_pdf)


def test_ask_missing_pdf_exits_nonzero(monkeypatch: pytest.MonkeyPatch, tmp_path, tmp_session_file):
    _monkeypatch_client(monkeypatch, "unused")
    missing = tmp_path / "nope.pdf"
    exit_code = cli.main(_global_flags(tmp_session_file) + ["ask", str(missing), "q"])
    assert exit_code == 1


def test_sessions_empty(monkeypatch: pytest.MonkeyPatch, tmp_session_file):
    monkeypatch.setattr(
        cli,
        "_storage_from_args",
        lambda args: cli.SessionStorage(tmp_session_file),
    )
    assert cli.main(_global_flags(tmp_session_file) + ["sessions"]) == 0


def test_show_and_delete(monkeypatch: pytest.MonkeyPatch, tmp_session_file):
    storage = cli.SessionStorage(tmp_session_file)
    entry = cli.QAEntry.new(
        pdf="sample.pdf",
        question="Q?",
        answer="A.",
        model="m",
        endpoint="e",
    )
    storage.add(entry)

    monkeypatch.setattr(
        cli,
        "_storage_from_args",
        lambda args: storage,
    )

    base = _global_flags(tmp_session_file)
    assert cli.main(base + ["show", entry.id]) == 0
    assert cli.main(base + ["show", "nope"]) == 1
    assert cli.main(base + ["delete", entry.id]) == 0
    assert storage.find(entry.id) is None
    assert cli.main(base + ["delete", entry.id]) == 1


def test_main_requires_command(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(SystemExit):
        cli.main([])
