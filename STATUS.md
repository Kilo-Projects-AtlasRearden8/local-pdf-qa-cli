# STATUS

local-pdf-qa-cli — local-first Python CLI that answers questions about local PDF
documents using a configurable OpenAI-compatible endpoint (default Ollama).
Commit: initial release.

## What was built

A small Python CLI (`local_pdf_qa` package) that lets you ask questions about
PDF documents on your own computer. Text is extracted locally with `pypdf`
(nothing is uploaded), the question is sent to a configurable OpenAI-compatible
endpoint (default Ollama at `http://localhost:11434/v1`), and each Q&A is saved
to a local JSON session file.

Modules:
- `cli.py` — argparse commands: `ask`, `sessions`, `show`, `delete`; global
  options `--endpoint`, `--model`, `--session-file`, `--api-key`,
  `--temperature`. Console script entry point: `local-pdf-qa-cli`.
- `__main__.py` — supports `python3 -m local_pdf_qa`.
- `config.py` — `AppConfig` and `load_config`: arguments beat environment
  variables beat built-in defaults; no API key required by default.
- `extract.py` — `extract_text` / `extract_pages`: local PDF text extraction
  with pypdf; `ExtractionError` when a PDF has no extractable text.
- `client.py` — `LLMClient`: talks to an OpenAI-compatible
  `/chat/completions` endpoint, optional Bearer API key, injectable
  `httpx.Client` for testing with a mock transport.
- `qa.py` — `answer_question`: extracts local PDF text, builds a plain-language
  prompt ("answer only using the provided document text"), and asks the model.
- `session.py` — `QAEntry` dataclass and `SessionStorage`: atomic read/write of
  Q&A entries to a local JSON file (temp file + `os.replace`).

Tests (`tests/`): `test_extract.py` (text extraction, missing file, textless
PDF), `test_client.py` (mock endpoint via `httpx.MockTransport`, model/
temperature payload, error handling, API key header), `test_session.py`
(storage round-trip, atomic write with no `.tmp` leftovers, corrupt/non-list
JSON), `test_qa.py` (answer_question with fake client and truncation),
`test_cli.py` (ask saves a session, missing PDF exits 1, sessions/show/delete).

Also included: `LICENSE` (MIT, "Copyright (c) 2026 Asdale Dynamics, LLC"),
`README.md` (credits Asdale Dynamics, LLC), `pyproject.toml`, `.gitignore`,
`STATUS.md`. Local-first, no network except your chosen endpoint, no secrets,
no API keys, no personal data.

## How to run

```bash
pip install -e . --break-system-packages   # installs local-pdf-qa-cli script
local-pdf-qa-cli --help

# Ask a question about a local PDF (default Ollama endpoint)
local-pdf-qa-cli --endpoint http://localhost:11434/v1 --model llama3 \
  ask paperwork.pdf "What is the total due?"

local-pdf-qa-cli sessions
local-pdf-qa-cli show <session-id>
local-pdf-qa-cli delete <session-id>

# Or without installing:
python3 -m local_pdf_qa --help
```

All Q&A sessions are saved to `qa_sessions.json` in the current directory
(use `--session-file` for another location). Nothing is uploaded.

## Verification results

- `pip install -e . --break-system-packages`: OK (console script
  `local-pdf-qa-cli` installed; package builds cleanly with setuptools)
- `python3 -m pytest -q`: 20 passed
- `python3 -m ruff check local_pdf_qa tests`: All checks passed
- `python3 -m ruff format --check local_pdf_qa tests`: All files formatted
- Manual end-to-end flow verified against a mock OpenAI-compatible server:
  `ask` (prints answer, saves session to JSON), `sessions`, `show`,
  `delete` (removed entry, "No Q&A sessions yet."), missing PDF exits 1.

Python 3.13.5; dependencies: pypdf 6.21.2, httpx 0.28.1.

## Known gaps

- Requires a running OpenAI-compatible endpoint (default Ollama) to answer;
  there is no bundled model. Tests use a mock endpoint, so no keys or network
  are needed.
- Only the `/chat/completions` (non-streaming) OpenAI-compatible shape is
  supported.
- Large PDFs are truncated to the first 12,000 characters of extracted text
  to keep prompts bounded.
- The answer is only as good as the endpoint's model and the extracted text;
  scanned/image-only PDFs may yield no extractable text.
- Session storage is a single flat JSON file; no search, filtering, or
  per-PDF grouping yet.
- No `.github/workflows` files (per project constraints), no CI configured.
