# Phase 5 — Retrieval layer

Implements [docs/rag-architecture.md](../../../docs/rag-architecture.md) **§5** (query preprocessing, dense retrieval, metadata filter, merge by `source_url`, primary citation selection).

## Run

From repository root (requires an index built by ingest phase **4.3** under `INGEST_CHROMA_DIR`, default `data/chroma`):

```bash
python -m runtime.phase_5_retrieval "What is the expense ratio for HDFC Mid Cap Fund?"
```

## API

```python
from runtime.phase_5_retrieval import retrieve, RetrievalResult

r: RetrievalResult = retrieve("Your question")
# r.contexts — merged text per source_url (for LLM §6)
# r.citation_url — single URL for §5.3 / §6.2
```

## Environment

Uses the same on-disk Chroma paths as ingest phase 4.3 (`INGEST_CHROMA_DIR`, `INGEST_CHROMA_COLLECTION`) and the same BGE query embedding as ingest (`INGEST_EMBEDDING_MODEL`, default `BAAI/bge-small-en-v1.5`).

| Variable | Purpose |
|----------|---------|
| `RETRIEVAL_TOP_K` | Chroma `n_results` (default `24`) |
| `INGEST_CHROMA_COLLECTION` | Collection name |
| `INGEST_CHROMA_DIR` | Chroma persist directory (default `data/chroma`) |
| `INGEST_REGISTRY_PATH` | `urls.yaml` for scheme resolution (§5.1) |

## Scope

- **In:** BGE query embedding, Chroma query, merge-by-URL, pick top citation.
- **Not in:** Router/refusal (§7), LLM generation (§6), thread store (§8) — wire those upstream.
