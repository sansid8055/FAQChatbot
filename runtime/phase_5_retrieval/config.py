"""Retrieval defaults (rag-architecture.md §5)."""

from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_ROOT = Path(__file__).resolve().parents[2]

# Must match ingest phase 4.2 / chunking-embedding-architecture.md (no import — avoids loading torch via ingest __init__).
EMBEDDING_MODEL_ID = os.environ.get("INGEST_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5").strip()
BGE_QUERY_PREFIX = "Represent this sentence: "


def repo_root() -> Path:
    p = os.environ.get("INGEST_REPO_ROOT")
    if p:
        return Path(p).expanduser().resolve()
    return _DEFAULT_ROOT


def url_registry_path() -> Path:
    p = os.environ.get("INGEST_REGISTRY_PATH")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "ingest" / "url_registry" / "urls.yaml"


def retrieval_top_k() -> int:
    return int(os.environ.get("RETRIEVAL_TOP_K", "24"))


def chroma_collection_name() -> str:
    return os.environ.get("INGEST_CHROMA_COLLECTION", "mf_faq_chunks").strip()
