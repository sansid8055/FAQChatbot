"""Phase 4.3: upsert chunk embeddings into Chroma."""

from ingest.phases.phase_4_3_vector_index.pipeline import (
    discover_latest_chunked_run,
    run_chroma_index,
)

__all__ = ["discover_latest_chunked_run", "run_chroma_index"]
