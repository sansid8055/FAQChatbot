"""Datatypes for retrieval results (rag-architecture.md §5)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MergedContext:
    """Several chunks merged for the same ``source_url`` (§5.2.4)."""

    source_url: str
    text: str
    distance: float
    scheme_id: str
    scheme_name: str
    fetched_at: str
    chunk_ids: list[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    """Output of phase 5 retrieval before LLM (§5–§6 boundary)."""

    query: str
    scheme_filter: str | None
    contexts: list[MergedContext]
    citation_url: str
    citation_fetched_at: str
    citation_scheme_id: str
