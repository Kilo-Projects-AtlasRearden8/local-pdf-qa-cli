"""Tests for local Q&A session storage."""

from __future__ import annotations

import json

from local_pdf_qa.session import QAEntry, SessionStorage


def _sample() -> QAEntry:
    return QAEntry.new(
        pdf="sample.pdf",
        question="What is the budget?",
        answer="One thousand dollars.",
        model="test-model",
        endpoint="http://mock/v1",
    )


def test_load_missing_file_returns_empty(tmp_path):
    storage = SessionStorage(tmp_path / "missing.json")
    assert storage.load() == []


def test_add_load_delete_roundtrip(tmp_path, tmp_session_file):
    storage = SessionStorage(tmp_session_file)
    entry = _sample()
    storage.add(entry)

    loaded = storage.load()
    assert len(loaded) == 1
    assert loaded[0].id == entry.id
    assert loaded[0].pdf == entry.pdf
    assert loaded[0].question == entry.question

    found = storage.find(entry.id)
    assert found is not None
    assert found.answer == "One thousand dollars."

    assert storage.delete(entry.id) is True
    assert storage.find(entry.id) is None
    assert storage.delete(entry.id) is False
    assert storage.load() == []


def test_save_writes_valid_json_and_no_tmp_leftovers(tmp_path, tmp_session_file):
    storage = SessionStorage(tmp_session_file)
    storage.add(_sample())

    files = [p.name for p in tmp_path.iterdir()]
    assert tmp_session_file.name in files
    assert not any(name.endswith(".tmp") for name in files)

    with tmp_session_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data[0]["id"] == storage.load()[0].id


def test_corrupt_file_returns_empty(tmp_path, tmp_session_file):
    storage = SessionStorage(tmp_session_file)
    tmp_session_file.write_text("{not valid json", encoding="utf-8")
    assert storage.load() == []


def test_non_list_json_returns_empty(tmp_path, tmp_session_file):
    storage = SessionStorage(tmp_session_file)
    tmp_session_file.write_text('{"not": "a list"}', encoding="utf-8")
    assert storage.load() == []
