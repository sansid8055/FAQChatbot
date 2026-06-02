"""Chroma vector index defaults (rag-architecture.md §4.3, chunking-embedding-architecture.md §9).

Does not import phase 4.2 so this package runs without PyTorch / sentence-transformers.
"""

from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_ROOT = Path(__file__).resolve().parents[3]


def repo_root() -> Path:
    p = os.environ.get("INGEST_REPO_ROOT")
    if p:
        return Path(p).expanduser().resolve()
    return _DEFAULT_ROOT


def chunked_dir() -> Path:
    p = os.environ.get("INGEST_CHUNKED_DIR")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "data" / "chunked"


def chroma_persist_dir() -> Path:
    p = os.environ.get("INGEST_CHROMA_DIR")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "data" / "chroma"


def chroma_collection_name() -> str:
    return os.environ.get("INGEST_CHROMA_COLLECTION", "mf_faq_chunks").strip()


def url_registry_path() -> Path:
    p = os.environ.get("INGEST_REGISTRY_PATH")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "ingest" / "url_registry" / "urls.yaml"


# Must match phase 4.2 frozen contract (same env var names).
EMBEDDING_DIMENSIONS = int(os.environ.get("INGEST_EMBEDDING_DIMENSIONS", "384"))

CHROMA_UPSERT_BATCH = int(os.environ.get("INGEST_CHROMA_UPSERT_BATCH", "64"))
