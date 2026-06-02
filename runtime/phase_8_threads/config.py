"""Phase 8 thread store configuration (rag-architecture.md §8)."""

from __future__ import annotations

import os
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def thread_db_path() -> Path:
    """SQLite path when ``THREAD_BACKEND=sqlite``; override with THREAD_DB_PATH."""
    raw = os.environ.get("THREAD_DB_PATH")
    if raw:
        return Path(raw).expanduser().resolve()
    return _repo_root() / "data" / "threads" / "threads.sqlite3"


def thread_max_turns() -> int:
    """Default last-N user turns considered for follow-up retrieval expansion (§8.2)."""
    return max(1, min(20, int(os.environ.get("THREAD_MAX_TURNS", "5"))))


def thread_expand_prior_users() -> int:
    """How many prior user utterances may be concatenated into the retrieval query."""
    return max(0, min(5, int(os.environ.get("THREAD_EXPAND_PRIOR_USERS", "2"))))
