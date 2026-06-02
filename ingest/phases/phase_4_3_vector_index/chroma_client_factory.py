"""Create a local Chroma ``PersistentClient`` (on-disk SQLite under ``INGEST_CHROMA_DIR``)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from ingest.phases.phase_4_3_vector_index import config


def create_chroma_client(
    *,
    chroma_persist: Path | None = None,
) -> tuple[Any, Path]:
    """
    Return ``(client, persist_path)`` for read/write against a local directory.

    Ingest (phase 4.3) and the runtime retriever both use this path so the index
    is portable and does not depend on any hosted vector service.
    """
    persist = (chroma_persist or config.chroma_persist_dir()).resolve()
    persist.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist))
    return client, persist
