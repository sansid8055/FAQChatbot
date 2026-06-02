"""Orchestrate thread messages with phase 7 ``answer()`` (rag-architecture.md §8)."""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

from runtime.phase_6_generation.types import GenerationResult
from runtime.phase_7_safety.pipeline import answer
from runtime.phase_8_threads.config import thread_expand_prior_users, thread_max_turns
from runtime.phase_8_threads.expand_query import expand_query_for_retrieval
from runtime.phase_8_threads.store import (
    append_message,
    list_messages,
    recent_messages_for_context,
    thread_exists,
)
from runtime.phase_8_threads.types import Message, ThreadNotFoundError

logger = logging.getLogger(__name__)

_post_lock_guard = threading.Lock()
_post_locks: dict[str, threading.Lock] = {}


def _post_message_lock(thread_id: str) -> threading.Lock:
    """Serialize turns for one thread; different threads do not share this lock."""
    with _post_lock_guard:
        lock = _post_locks.get(thread_id)
        if lock is None:
            lock = threading.Lock()
            _post_locks[thread_id] = lock
        return lock


def _debug_payload_from_generation(g: GenerationResult) -> str:
    return json.dumps(
        {
            "model": g.model,
            "validation_ok": g.validation_ok,
            "fallback_used": g.fallback_used,
            "advisory_refusal": g.advisory_refusal,
            "router_reason": g.router_reason,
        },
        separators=(",", ":"),
    )


def post_user_message(
    thread_id: str,
    content: str,
    *,
    expand_for_retrieval: bool = True,
    registry_path: Path | None = None,
    block_on_pii_in_query: bool = True,
) -> tuple[Message, Message]:
    """
    Append the user line, run §7 ``answer()`` on an optionally expanded query, append assistant.

    Returns ``(user_message, assistant_message)`` as stored rows.
    """
    with _post_message_lock(thread_id):
        if not thread_exists(thread_id):
            raise ThreadNotFoundError(thread_id)

        history = list_messages(thread_id)
        if expand_for_retrieval:
            q = expand_query_for_retrieval(
                content,
                history,
                max_prior_user_utterances=thread_expand_prior_users(),
            )
        else:
            q = content.strip()

        if q != content.strip():
            logger.debug("Retrieval query expanded for thread %s", thread_id[:8])

        g = answer(
            q,
            registry_path=registry_path,
            block_on_pii_in_query=block_on_pii_in_query,
        )
        user_row = append_message(thread_id, "user", content.strip())
        asst_row = append_message(
            thread_id,
            "assistant",
            g.user_visible,
            retrieval_debug_id=_debug_payload_from_generation(g),
        )
        return user_row, asst_row


def context_messages_for_thread(thread_id: str) -> list[Message]:
    """Last-N-turn window for UI or future context packing (§8.2)."""
    if not thread_exists(thread_id):
        raise ThreadNotFoundError(thread_id)
    return recent_messages_for_context(thread_id, max_turns=thread_max_turns())
