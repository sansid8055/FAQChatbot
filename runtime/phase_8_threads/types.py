"""Phase 8 domain types (rag-architecture.md §8.1)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Thread:
    """Opaque thread id + optional non-PII session key (§8.1)."""

    id: str
    session_key: str | None
    created_at: str


@dataclass(frozen=True)
class Message:
    """One chat row: role, content, time, optional retrieval debug id (§8.1)."""

    id: int
    thread_id: str
    role: str
    content: str
    created_at: str
    retrieval_debug_id: str | None


class ThreadNotFoundError(LookupError):
    """Raised when a thread id is missing from the store."""
