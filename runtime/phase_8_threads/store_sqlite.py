"""SQLite-backed thread and message persistence (optional: THREAD_BACKEND=sqlite)."""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from runtime.phase_8_threads.config import thread_db_path
from runtime.phase_8_threads.types import Message, Thread


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _connect() -> sqlite3.Connection:
    path = thread_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS threads (
            id TEXT PRIMARY KEY,
            session_key TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            retrieval_debug_id TEXT,
            FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id, id);
        """
    )
    conn.commit()


def ensure_schema() -> None:
    with _connect() as conn:
        init_schema(conn)


def create_thread(*, session_key: str | None = None) -> str:
    ensure_schema()
    tid = str(uuid.uuid4())
    now = _utc_now_iso()
    with _connect() as conn:
        init_schema(conn)
        conn.execute(
            "INSERT INTO threads (id, session_key, created_at) VALUES (?, ?, ?)",
            (tid, session_key, now),
        )
        conn.commit()
    return tid


def thread_exists(thread_id: str) -> bool:
    ensure_schema()
    with _connect() as conn:
        init_schema(conn)
        row = conn.execute("SELECT 1 FROM threads WHERE id = ?", (thread_id,)).fetchone()
    return row is not None


def get_thread(thread_id: str) -> Thread | None:
    ensure_schema()
    with _connect() as conn:
        init_schema(conn)
        row = conn.execute(
            "SELECT id, session_key, created_at FROM threads WHERE id = ?",
            (thread_id,),
        ).fetchone()
    return _row_thread(row) if row else None


def list_threads(*, session_key: str | None = None) -> list[Thread]:
    ensure_schema()
    with _connect() as conn:
        init_schema(conn)
        if session_key is None:
            rows = conn.execute(
                "SELECT id, session_key, created_at FROM threads ORDER BY created_at DESC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, session_key, created_at FROM threads WHERE session_key = ? "
                "ORDER BY created_at DESC",
                (session_key,),
            ).fetchall()
    return [_row_thread(r) for r in rows]


def list_messages(thread_id: str) -> list[Message]:
    ensure_schema()
    with _connect() as conn:
        init_schema(conn)
        rows = conn.execute(
            "SELECT id, thread_id, role, content, created_at, retrieval_debug_id "
            "FROM messages WHERE thread_id = ? ORDER BY id ASC",
            (thread_id,),
        ).fetchall()
    return [_row_message(r) for r in rows]


def append_message(
    thread_id: str,
    role: str,
    content: str,
    *,
    retrieval_debug_id: str | None = None,
) -> Message:
    ensure_schema()
    now = _utc_now_iso()
    with _connect() as conn:
        init_schema(conn)
        cur = conn.execute(
            "INSERT INTO messages (thread_id, role, content, created_at, retrieval_debug_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (thread_id, role, content, now, retrieval_debug_id),
        )
        mid = int(cur.lastrowid)
        conn.commit()
    return Message(
        id=mid,
        thread_id=thread_id,
        role=role,
        content=content,
        created_at=now,
        retrieval_debug_id=retrieval_debug_id,
    )


def recent_messages_for_context(thread_id: str, *, max_turns: int) -> list[Message]:
    all_msgs = list_messages(thread_id)
    cap = max(1, max_turns) * 2
    return all_msgs[-cap:] if len(all_msgs) > cap else all_msgs


def _row_thread(r: sqlite3.Row) -> Thread:
    return Thread(id=r["id"], session_key=r["session_key"], created_at=r["created_at"])


def _row_message(r: sqlite3.Row) -> Message:
    return Message(
        id=r["id"],
        thread_id=r["thread_id"],
        role=r["role"],
        content=r["content"],
        created_at=r["created_at"],
        retrieval_debug_id=r["retrieval_debug_id"],
    )
