"""End-to-end retrieval entrypoint (rag-architecture.md §5)."""

from __future__ import annotations

from pathlib import Path

from runtime.phase_5_retrieval import config
from runtime.phase_5_retrieval.chroma_access import get_query_collection
from runtime.phase_5_retrieval.embed_query import embed_query
from runtime.phase_5_retrieval.preprocess import resolve_scheme_filter
from runtime.phase_5_retrieval.retrieve import retrieve_from_chroma
from runtime.phase_5_retrieval.types import RetrievalResult


def retrieve(
    query: str,
    *,
    registry_path: Path | None = None,
) -> RetrievalResult:
    """
    Preprocess → embed query → Chroma dense retrieval → merge by URL → select citation (§5.3).

    Reads the on-disk Chroma store under ``INGEST_CHROMA_DIR`` (same as ingest phase 4.3).
    """
    reg = registry_path or config.url_registry_path()
    scheme_filter = resolve_scheme_filter(query, reg)

    q_emb = embed_query(query)
    collection = get_query_collection()
    return retrieve_from_chroma(
        collection,
        query,
        q_emb,
        scheme_filter=scheme_filter,
    )
