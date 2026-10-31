"""Allow running the CLI as ``python -m local_pdf_qa``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
