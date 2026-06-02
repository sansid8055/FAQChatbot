"""Phase 9 HTTP API configuration (rag-architecture.md §9)."""

from __future__ import annotations

import os


def api_debug_enabled() -> bool:
    """When true, responses may include ``debug`` and message ``retrieval_debug_id`` (§9.2)."""
    return os.environ.get("RUNTIME_API_DEBUG", "").strip().lower() in ("1", "true", "yes", "on")


def admin_reindex_secret() -> str | None:
    """Bearer token for ``POST /admin/reindex``; unset disables the route (503)."""
    s = os.environ.get("ADMIN_REINDEX_SECRET", "").strip()
    return s or None


def api_host() -> str:
    return os.environ.get("API_HOST", "127.0.0.1").strip() or "127.0.0.1"


def api_port() -> int:
    return int(os.environ.get("PORT", os.environ.get("API_PORT", "8765")))
