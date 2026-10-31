"""Local JSON storage for Q&A sessions (atomic read/write)."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass
class QAEntry:
    """One saved question/answer about a PDF."""

    id: str
    pdf: str
    question: str
    answer: str
    model: str
    endpoint: str
    created_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pdf": self.pdf,
            "question": self.question,
            "answer": self.answer,
            "model": self.model,
            "endpoint": self.endpoint,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> QAEntry:
        return cls(
            id=data["id"],
            pdf=data["pdf"],
            question=data["question"],
            answer=data["answer"],
            model=data["model"],
            endpoint=data["endpoint"],
            created_at=data.get("created_at", ""),
        )

    @classmethod
    def new(
        cls,
        *,
        pdf: str,
        question: str,
        answer: str,
        model: str,
        endpoint: str,
    ) -> QAEntry:
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            id=str(uuid4())[:8],
            pdf=pdf,
            question=question,
            answer=answer,
            model=model,
            endpoint=endpoint,
            created_at=now,
        )


class SessionStorage:
    """Read/write Q&A entries to a local JSON file, written atomically."""

    def __init__(self, path: str | os.PathLike[str] = "qa_sessions.json") -> None:
        self.path = Path(path)

    def load(self) -> list[QAEntry]:
        """Load all entries; returns an empty list for missing or bad files."""
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return []
        if not isinstance(data, list):
            return []
        entries: list[QAEntry] = []
        for item in data:
            try:
                entries.append(QAEntry.from_dict(item))
            except (KeyError, TypeError):
                continue
        return entries

    def save(self, entries: list[QAEntry]) -> None:
        """Atomically write ``entries`` to the storage file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [entry.to_dict() for entry in entries]
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), prefix=".qa-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            os.replace(tmp, self.path)
        except BaseException:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise

    def add(self, entry: QAEntry) -> None:
        entries = self.load()
        entries.append(entry)
        self.save(entries)

    def find(self, entry_id: str) -> QAEntry | None:
        for entry in self.load():
            if entry.id == entry_id:
                return entry
        return None

    def delete(self, entry_id: str) -> bool:
        entries = self.load()
        filtered = [e for e in entries if e.id != entry_id]
        if len(filtered) == len(entries):
            return False
        self.save(filtered)
        return True
