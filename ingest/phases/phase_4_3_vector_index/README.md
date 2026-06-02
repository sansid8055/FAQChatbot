# Phase 4.3 — Vector index (local Chroma)

Upserts phase **4.2** outputs (`chunks.jsonl` + `embeddings.jsonl`) into an on-disk Chroma database via `chromadb.PersistentClient` under **`INGEST_CHROMA_DIR`** (default **`data/chroma`**). Ingest and the runtime retriever (phase 5) read the **same** directory — no hosted vector service or API keys.

## Run

```bash
python -m ingest.phases.phase_4_3_vector_index
# or: python -m ingest.phases.phase_4_3_vector_index --run-id <run_id>
# or: python -m ingest.phases.phase_4_3_vector_index --chroma-dir /path/to/chroma
```

## Outputs

- **`data/chunked/<run_id>/chroma_index_manifest.json`** — collection name, counts, `chroma_persist_path`, embedding model id.
- **`data/chroma/index_manifest.json`** — mirror copy next to the SQLite-backed index.

## Environment

| Variable | Purpose |
|----------|---------|
| `INGEST_CHROMA_DIR` | Persist directory (default `data/chroma`) |
| `INGEST_CHROMA_COLLECTION` | Collection name (default `mf_faq_chunks`) |
| `INGEST_CHROMA_UPSERT_BATCH` | Batch size (default `64`) |
| `INGEST_REGISTRY_PATH` | URL registry for purge-by-allowlist (default `ingest/url_registry/urls.yaml`) |
| `INGEST_CHUNKED_DIR` | Base for `--run-id` discovery (default `data/chunked`) |

## GitHub Actions

The daily workflow runs this phase and uploads **`data/chroma/`** as an artifact (`ingest-chroma-<run_id>`) so you can download the built index or attach it to a deployment step.
