"""Load repository-root ``.env`` for local development (optional)."""

from __future__ import annotations

from pathlib import Path


def load_repo_dotenv() -> None:
    """If ``python-dotenv`` is installed and ``<repo>/.env`` exists, load it.

    Does not override variables already set in the process environment.
    """
    try:
        from dotenv import load_dotenv as _load
    except ImportError:
        return
    root = Path(__file__).resolve().parent.parent
    path = root / ".env"
    if path.is_file():
        _load(path, override=False)
