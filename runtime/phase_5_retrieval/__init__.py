"""Phase 5 — Retrieval layer (rag-architecture.md §5)."""

from runtime.phase_5_retrieval.types import MergedContext, RetrievalResult

__all__ = ["retrieve", "MergedContext", "RetrievalResult"]


def __getattr__(name: str):
    if name == "retrieve":
        from runtime.phase_5_retrieval.pipeline import retrieve

        return retrieve
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
