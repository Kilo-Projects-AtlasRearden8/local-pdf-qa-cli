"""Tests for local PDF text extraction."""

from __future__ import annotations

from local_pdf_qa.extract import ExtractionError, extract_text


def test_extract_text_returns_sample_text(sample_pdf):
    text = extract_text(sample_pdf)
    assert "Project Alpha budget" in text
    assert "one thousand dollars" in text
    assert "Monday" in text


def test_extract_text_missing_file(tmp_path):
    missing = tmp_path / "does-not-exist.pdf"
    try:
        extract_text(missing)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError for missing file")


def test_extract_text_empty_pdf(tmp_path):
    from conftest import _make_pdf_bytes

    empty_pdf = tmp_path / "empty.pdf"
    empty_pdf.write_bytes(_make_pdf_bytes(""))
    try:
        extract_text(empty_pdf)
    except ExtractionError:
        pass
    else:
        raise AssertionError("Expected ExtractionError for textless PDF")
