"""Local embedding via sentence-transformers (BAAI/bge-small-en-v1.5)."""

from __future__ import annotations

import logging
from typing import Any

from sentence_transformers import SentenceTransformer

from ingest.phases.phase_4_2_chunk_embedding.config import EMBEDDING_MODEL_ID
from ingest.phases.phase_4_2_chunk_embedding.types import ChunkRecord

logger = logging.getLogger(__name__)

BATCH_SIZE = 32

_MODEL: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _MODEL  # noqa: PLW0603
    if _MODEL is None:
        logger.info("Loading sentence-transformers model %s", EMBEDDING_MODEL_ID)
        _MODEL = SentenceTransformer(EMBEDDING_MODEL_ID)
    return _MODEL


def embed_chunks(chunks: list[ChunkRecord]) -> list[dict[str, Any]]:
    """
    Return list of {chunk_id, embedding: list[float]} aligned with input order.
    Passages are embedded without prefix (BGE convention).
    """
    if not chunks:
        return []
    model = _get_model()
    texts = [c.chunk_text for c in chunks]
    logger.info("Encoding %d chunks (batch_size=%d)", len(texts), BATCH_SIZE)
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    out: list[dict[str, Any]] = []
    for c, vec in zip(chunks, embeddings, strict=True):
        out.append({"chunk_id": c.chunk_id, "embedding": vec.tolist()})
    return out


def embed_query(query: str) -> list[float]:
    """Embed a single user query with the BGE retrieval prefix."""
    from ingest.phases.phase_4_2_chunk_embedding.config import BGE_QUERY_PREFIX

    model = _get_model()
    vec = model.encode(
        BGE_QUERY_PREFIX + query,
        normalize_embeddings=True,
    )
    return vec.tolist()
