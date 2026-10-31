"""Local PDF text extraction using pypdf (nothing is uploaded)."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class ExtractionError(RuntimeError):
    """Raised when a PDF cannot be read or contains no extractable text."""


def extract_text(pdf_path: str | Path) -> str:
    """Extract all text from a PDF file on the local machine.

    The file is read from disk only; nothing is uploaded anywhere.
    """
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            parts.append(text)
    full = "\n".join(parts).strip()
    if not full:
        raise ExtractionError(f"No extractable text found in {pdf_path}")
    return full


def extract_pages(pdf_path: str | Path) -> list[str]:
    """Return per-page text for a local PDF."""
    reader = PdfReader(str(pdf_path))
    return [page.extract_text() or "" for page in reader.pages]
