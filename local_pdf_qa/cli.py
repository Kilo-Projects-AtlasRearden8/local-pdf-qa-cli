"""Command-line interface for local-pdf-qa-cli."""

from __future__ import annotations

import argparse
import sys

from .client import LLMClient
from .config import load_config
from .qa import answer_question
from .session import QAEntry, SessionStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local-pdf-qa-cli",
        description="Ask questions about local PDF documents using a local-first "
        "OpenAI-compatible endpoint (default Ollama). Nothing is uploaded.",
    )
    parser.add_argument(
        "--endpoint",
        default=None,
        help="OpenAI-compatible endpoint base URL (default: http://localhost:11434/v1)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name (default: llama3)",
    )
    parser.add_argument(
        "--session-file",
        default=None,
        help="Local JSON file for saved Q&A sessions (default: qa_sessions.json)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Optional API key (Bearer) for endpoints that require one",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Sampling temperature (default: 0.3)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_ask = sub.add_parser("ask", help="Ask a question about a local PDF")
    p_ask.add_argument("pdf", help="Path to the local PDF file")
    p_ask.add_argument("question", help="Question to ask about the PDF")

    sub.add_parser("sessions", help="List saved Q&A sessions")

    p_show = sub.add_parser("show", help="Show a saved Q&A session")
    p_show.add_argument("id", help="Session entry ID")

    p_delete = sub.add_parser("delete", help="Delete a saved Q&A session")
    p_delete.add_argument("id", help="Session entry ID")
    return parser


def _client_from_args(args: argparse.Namespace) -> LLMClient:
    config = load_config(
        endpoint=args.endpoint,
        model=args.model,
        session_file=args.session_file,
        temperature=args.temperature,
        api_key=args.api_key,
    )
    return LLMClient(
        endpoint=config.endpoint,
        model=config.model,
        temperature=config.temperature,
        api_key=config.api_key,
    )


def _storage_from_args(args: argparse.Namespace) -> SessionStorage:
    config = load_config(session_file=args.session_file)
    return SessionStorage(config.session_file)


def cmd_ask(args: argparse.Namespace) -> int:
    client = _client_from_args(args)
    storage = _storage_from_args(args)
    try:
        answer = answer_question(
            client=client,
            pdf_path=args.pdf,
            question=args.question,
        )
    except FileNotFoundError as exc:
        print(f"Error: PDF not found: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - surface endpoint errors to the user
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(answer)
    print()
    entry = QAEntry.new(
        pdf=args.pdf,
        question=args.question,
        answer=answer,
        model=client.model,
        endpoint=client.endpoint,
    )
    storage.add(entry)
    print(f"Saved Q&A session {entry.id} to {storage.path}")
    return 0


def cmd_sessions(args: argparse.Namespace) -> int:
    storage = _storage_from_args(args)
    entries = storage.load()
    if not entries:
        print("No Q&A sessions yet.")
        return 0
    for entry in entries:
        print(
            f"{entry.id}  {entry.created_at[:10]}  {entry.pdf}  "
            f"model={entry.model}  endpoint={entry.endpoint}"
        )
        print(f"    Q: {entry.question}")
        print(f"    A: {entry.answer[:120]}{'...' if len(entry.answer) > 120 else ''}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    storage = _storage_from_args(args)
    entry = storage.find(args.id)
    if entry is None:
        print(f"Session not found: {args.id}", file=sys.stderr)
        return 1
    print(f"ID:        {entry.id}")
    print(f"Created:   {entry.created_at}")
    print(f"PDF:       {entry.pdf}")
    print(f"Model:     {entry.model}")
    print(f"Endpoint:  {entry.endpoint}")
    print()
    print(f"Question: {entry.question}")
    print()
    print(f"Answer: {entry.answer}")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    storage = _storage_from_args(args)
    if storage.delete(args.id):
        print(f"Deleted session {args.id}")
        return 0
    print(f"Session not found: {args.id}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    commands = {
        "ask": cmd_ask,
        "sessions": cmd_sessions,
        "show": cmd_show,
        "delete": cmd_delete,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
