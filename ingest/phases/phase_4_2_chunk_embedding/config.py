"""Chunk + embed defaults (chunking-embedding-architecture.md §4.1).

Model: BAAI/bge-small-en-v1.5 — 384-dim, 512 max tokens, BERT WordPiece tokenizer.
Lightweight and sufficient for the current corpus (~5 small structured scheme pages).
Upgrade path: swap to bge-base-en-v1.5 (768-dim) when the corpus grows; requires full re-embed.
"""

from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_ROOT = Path(__file__).resolve().parents[3]

# Frozen embedding contract (change only with full re-embed).
EMBEDDING_MODEL_ID = os.environ.get(
    "INGEST_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"
).strip()
EMBEDDING_DIMENSIONS = int(os.environ.get("INGEST_EMBEDDING_DIMENSIONS", "384"))
MAX_INPUT_TOKENS = int(os.environ.get("INGEST_EMBED_MAX_INPUT_TOKENS", "512"))

# Chunk packing (tuned for 512-token model)
TARGET_TOKENS = int(os.environ.get("INGEST_CHUNK_TARGET_TOKENS", "400"))
MAX_TOKENS = int(os.environ.get("INGEST_CHUNK_MAX_TOKENS", "460"))
OVERLAP_TOKENS = int(os.environ.get("INGEST_CHUNK_OVERLAP_TOKENS", "50"))

# BGE query prefix (passages get no prefix)
BGE_QUERY_PREFIX = "Represent this sentence: "


def repo_root() -> Path:
    p = os.environ.get("INGEST_REPO_ROOT")
    if p:
        return Path(p).expanduser().resolve()
    return _DEFAULT_ROOT


def normalized_dir() -> Path:
    p = os.environ.get("INGEST_NORMALIZED_DIR")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "data" / "normalized"


def chunked_output_dir() -> Path:
    p = os.environ.get("INGEST_CHUNKED_DIR")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "data" / "chunked"
