"""Fixtures for local-pdf-qa-cli tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader

SAMPLE_TEXT = (
    "The Massive AI Manual sample page. "
    "Project Alpha budget is one thousand dollars. "
    "Team meeting is on Monday morning."
)


def _make_pdf_bytes(text: str) -> bytes:
    """Build a minimal valid PDF containing ``text`` (no upload, local only)."""
    buf = bytearray()
    offsets: dict[int, int] = {}
    buf += b"%PDF-1.4\n"

    def obj(num: int, content: bytes, stream: bytes | None = None) -> None:
        nonlocal buf
        offsets[num] = len(buf)
        buf += f"{num} 0 obj\n".encode("ascii")
        if stream is not None:
            buf += b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\n"
            buf += b"stream\n" + stream + b"\nendstream\n"
        else:
            buf += content + b"\n"
        buf += b"endobj\n"

    obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1", "replace")
    obj(4, b"", stream=content)
    obj(
        3,
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
    )
    obj(5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    xref_offset = len(buf)
    buf += b"xref\n0 6\n"
    buf += b"0000000000 65535 f \n"
    for num in (1, 2, 3, 4, 5):
        buf += f"{offsets[num]:010d} 00000 n \n".encode("ascii")
    buf += b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
    buf += f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    return bytes(buf)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(_make_pdf_bytes(SAMPLE_TEXT))
    # Sanity check: pypdf can read it back.
    reader = PdfReader(str(pdf_path))
    assert len(reader.pages) == 1
    return pdf_path


@pytest.fixture
def tmp_session_file(tmp_path: Path) -> Path:
    return tmp_path / "qa_sessions.json"
