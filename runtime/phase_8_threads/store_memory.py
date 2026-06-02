"""In-process thread/message store: no disk I/O; data is lost on process exit (default)."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone

from runtime.phase_8_threads.types import Message, Thread

_lock = threading.RLock()
_threads: dict[str, Thread] = {}
_messages: dict[str, list[Message]] = {}
_next_msg_id: dict[str, int] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def reset_memory_store_for_tests() -> None:
    """Clear all threads (unittest isolation)."""
    with _lock:
        _threads.clear()
        _messages.clear()
        _next_msg_id.clear()


def ensure_schema() -> None:
    """No-op (API lifespan compatibility)."""
    return


def create_thread(*, session_key: str | None = None) -> str:
    tid = str(uuid.uuid4())
    now = _utc_now_iso()
    t = Thread(id=tid, session_key=session_key, created_at=now)
    with _lock:
        _threads[tid] = t
        _messages[tid] = []
        _next_msg_id[tid] = 1
    return tid


def thread_exists(thread_id: str) -> bool:
    with _lock:
        return thread_id in _threads


def get_thread(thread_id: str) -> Thread | None:
    with _lock:
        return _threads.get(thread_id)


def list_threads(*, session_key: str | None = None) -> list[Thread]:
    with _lock:
        rows = list(_threads.values())
    if session_key is not None:
        rows = [t for t in rows if t.session_key == session_key]
    rows.sort(key=lambda t: t.created_at, reverse=True)
    return rows


def list_messages(thread_id: str) -> list[Message]:
    with _lock:
        return list(_messages.get(thread_id, []))


def append_message(
    thread_id: str,
    role: str,
    content: str,
    *,
    retrieval_debug_id: str | None = None,
) -> Message:
    now = _utc_now_iso()
    with _lock:
        if thread_id not in _threads:
            raise KeyError(thread_id)
        mid = _next_msg_id[thread_id]
        _next_msg_id[thread_id] = mid + 1
        m = Message(
            id=mid,
            thread_id=thread_id,
            role=role,
            content=content,
            created_at=now,
            retrieval_debug_id=retrieval_debug_id,
        )
        _messages[thread_id].append(m)
    return m


def recent_messages_for_context(thread_id: str, *, max_turns: int) -> list[Message]:
    all_msgs = list_messages(thread_id)
    cap = max(1, max_turns) * 2
    return all_msgs[-cap:] if len(all_msgs) > cap else all_msgs
