# local-pdf-qa-cli

A local-first Python CLI that answers questions about your local PDF documents
using a configurable OpenAI-compatible endpoint (default Ollama). Your PDFs
never leave your machine: text is extracted locally, and your Q&A sessions are
saved to a local JSON file. No accounts, no API keys required by default, and
nothing is ever uploaded.

A project by **Dylan Asdale / Asdale Dynamics, LLC** (Indiana, formed October
2026). Dylan is a registered nurse turned AI author; his book *The Massive AI
Manual* and hub site dylanasdale.github.io explain AI "like a friend would":
plain English, step by step, never condescending. Asdale Dynamics, LLC focuses
on beginner-friendly AI education, books and guides, and practical local-first
tools.

Built for beginners: everything runs on your own computer, there are no secrets
or API keys in the code, and no personal data is collected.

## Install

You need Python 3.10 or newer. Get a copy of this project, then install it:

```bash
git clone <this-repo>
cd local-pdf-qa-cli
pip install -e .
```

The `pypdf` and `httpx` packages are installed automatically. `pypdf` does the
local PDF text extraction and `httpx` talks to your OpenAI-compatible endpoint.

## How it works

1. You point the CLI at a PDF on your computer and ask a question.
2. The CLI extracts the PDF's text locally with `pypdf` (nothing is uploaded).
3. It sends the document text and your question to an OpenAI-compatible
   `/chat/completions` endpoint (default Ollama at
   `http://localhost:11434/v1`).
4. It prints the answer and saves the question, answer, model, and endpoint to
   a local JSON session file (`qa_sessions.json` by default).

## Usage

Global options (place these before the subcommand):

```bash
local-pdf-qa-cli --endpoint http://localhost:11434/v1 --model llama3 ...
```

### Ask a question about a PDF

```bash
local-pdf-qa-cli --endpoint http://localhost:11434/v1 --model llama3 \
  ask paperwork.pdf "What is the total due on this invoice?"
```

The answer is printed, then saved as a new Q&A session.

### List saved Q&A sessions

```bash
local-pdf-qa-cli sessions
```

### Show one saved session

```bash
local-pdf-qa-cli show <session-id>
```

### Delete a saved session

```bash
local-pdf-qa-cli delete <session-id>
```

### Options

| Option | Meaning |
|--------|---------|
| `--endpoint` | OpenAI-compatible endpoint base URL (default: `http://localhost:11434/v1`) |
| `--model` | Model name (default: `llama3`) |
| `--session-file` | Local JSON file for saved Q&A sessions (default: `qa_sessions.json`) |
| `--api-key` | Optional Bearer API key for endpoints that require one |
| `--temperature` | Sampling temperature (default: 0.3) |

You can also run without installing: `python3 -m local_pdf_qa --help`.

## Storage

All Q&A sessions live in a local JSON file (`qa_sessions.json` by default,
changeable with `--session-file`). Writes are atomic (temp file + replace), so
a crash won't leave a half-written file. Nothing is sent anywhere; there is no
network requirement beyond your chosen endpoint.

## Tests

Tests use a mock endpoint — no network and no API keys:

```bash
pip install pytest
pytest
```

## Credits

Built by Dylan Asdale, registered nurse turned AI author and founder of
**Asdale Dynamics, LLC** — beginner-friendly AI education, books and guides,
and practical local-first tools. See *The Massive AI Manual* and
dylanasdale.github.io.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
