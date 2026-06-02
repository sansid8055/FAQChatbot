"""Phase 4.2: chunk normalized text + local BGE embeddings."""

from ingest.phases.phase_4_2_chunk_embedding.pipeline import (
    discover_latest_normalized_run,
    run_chunk_embed,
)

__all__ = ["discover_latest_normalized_run", "run_chunk_embed"]
