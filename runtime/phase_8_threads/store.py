"""Thread/message store: in-memory (default) or SQLite (THREAD_BACKEND=sqlite)."""

from __future__ import annotations

import os

_BACKEND = os.environ.get("THREAD_BACKEND", "memory").strip().lower()

if _BACKEND == "sqlite":
    from runtime.phase_8_threads.store_sqlite import (
        append_message,
        create_thread,
        ensure_schema,
        get_thread,
        list_messages,
        list_threads,
        recent_messages_for_context,
        thread_exists,
    )
else:
    from runtime.phase_8_threads.store_memory import (
        append_message,
        create_thread,
        ensure_schema,
        get_thread,
        list_messages,
        list_threads,
        recent_messages_for_context,
        reset_memory_store_for_tests,
        thread_exists,
    )

__all__ = [
    "append_message",
    "create_thread",
    "ensure_schema",
    "get_thread",
    "list_messages",
    "list_threads",
    "recent_messages_for_context",
    "thread_exists",
]

if _BACKEND != "sqlite":
    __all__.append("reset_memory_store_for_tests")
