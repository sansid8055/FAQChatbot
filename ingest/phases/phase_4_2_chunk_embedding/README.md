# Phase 4.2 — Chunk & embed

Implements [docs/chunking-embedding-architecture.md](../../../docs/chunking-embedding-architecture.md) (§3–4) and feeds phase **4.3** (vector index).

## Behaviour

1. Reads `data/normalized/<run_id>/normalize_manifest.json` and `scheme_facts.json`.
2. Splits each `*.txt` on `## ` headings → **sections**, then **greedy token-packs** with **tiktoken** `cl100k_base` (`TARGET_TOKENS` / `MAX_TOKENS` / `OVERLAP_TOKENS` from env or defaults).
3. Writes `data/chunked/<run_id>/chunks.jsonl` (one JSON object per line: full chunk metadata + `chunk_text`).
4. Embeds locally with **`BAAI/bge-small-en-v1.5`** via `sentence-transformers` (no API key needed) → `embeddings.jsonl` (`chunk_id` + `embedding`, 384-dim). Pass `--no-embed` to skip.
5. Writes `chunk_run_manifest.json`.

## CLI

```bash
# Chunk + embed (default — runs bge-small locally)
python3 -m ingest.phases.phase_4_2_chunk_embedding

# Chunks only (skip embedding)
python3 -m ingest.phases.phase_4_2_chunk_embedding --no-embed

# Specific run
python3 -m ingest.phases.phase_4_2_chunk_embedding --run-id 20260412T060804
```

## Environment

| Variable | Purpose |
|----------|---------|
| `INGEST_NORMALIZED_DIR` | Input base (default `data/normalized`) |
| `INGEST_CHUNKED_DIR` | Output base (default `data/chunked`) |
| `INGEST_EMBEDDING_MODEL` | Default `BAAI/bge-small-en-v1.5` |
| `INGEST_CHUNK_TARGET_TOKENS` | Default `600` |
| `INGEST_CHUNK_MAX_TOKENS` | Default `690` |
| `INGEST_CHUNK_OVERLAP_TOKENS` | Default `80` |
| `HF_HOME` | Hugging Face model cache dir (optional) |

## Next phase

Vector upsert: [phase_4_3_vector_index](../phase_4_3_vector_index/).
