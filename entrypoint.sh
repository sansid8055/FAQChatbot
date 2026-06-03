#!/bin/sh
set -e

# On first deploy (or after a clean volume), ChromaDB will be empty.
# Run the full ingest pipeline to populate it before starting the API server.
if [ ! -f /app/data/chroma/chroma.sqlite3 ]; then
  echo "[entrypoint] ChromaDB not found — running ingest pipeline..."
  python -m ingest.phases.phase_4_0_scheduler_scraping
  python -m ingest.phases.phase_4_1_normalize
  python -m ingest.phases.phase_4_2_chunk_embedding
  python -m ingest.phases.phase_4_3_vector_index
  echo "[entrypoint] Ingest complete."
else
  echo "[entrypoint] ChromaDB found — skipping ingest."
fi

exec python -m runtime.phase_9_api
