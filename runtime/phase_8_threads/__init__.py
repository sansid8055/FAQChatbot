"""Multi-thread chat store and orchestration (rag-architecture.md §8)."""

from __future__ import annotations

from runtime.phase_8_threads.expand_query import expand_query_for_retrieval
from runtime.phase_8_threads.store import (
    append_message,
    create_thread,
    get_thread,
    list_messages,
    list_threads,
    recent_messages_for_context,
    thread_exists,
)
from runtime.phase_8_threads.types import Message, Thread, ThreadNotFoundError

__all__ = [
    "Message",
    "Thread",
    "ThreadNotFoundError",
    "append_message",
    "context_messages_for_thread",
    "create_thread",
    "get_thread",
    "expand_query_for_retrieval",
    "list_messages",
    "list_threads",
    "post_user_message",
    "recent_messages_for_context",
    "thread_exists",
]


def __getattr__(name: str):
    """Lazy-import chat orchestration so importing ``store`` does not load retrieval/LLM."""
    if name == "context_messages_for_thread":
        from runtime.phase_8_threads.chat_service import context_messages_for_thread

        return context_messages_for_thread
    if name == "post_user_message":
        from runtime.phase_8_threads.chat_service import post_user_message

        return post_user_message
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
