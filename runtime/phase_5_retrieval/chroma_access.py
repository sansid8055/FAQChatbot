"""Read-only Chroma collection handle (reuses one PersistentClient — faster than per-request clients)."""

from __future__ import annotations

import threading
from typing import Any

from ingest.phases.phase_4_3_vector_index.chroma_client_factory import create_chroma_client

from runtime.phase_5_retrieval import config

_lock = threading.Lock()
_collection: Any | None = None


def get_query_collection() -> Any:
    """Return existing collection; raises if missing. Cached for the process lifetime."""
    global _collection
    with _lock:
        if _collection is None:
            client, _persist = create_chroma_client()
            name = config.chroma_collection_name()
            _collection = client.get_collection(name)
        return _collection
