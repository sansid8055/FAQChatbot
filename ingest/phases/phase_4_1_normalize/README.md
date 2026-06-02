# Phase 4.1 — Normalize HTML

Implements [docs/rag-architecture.md](../../../docs/rag-architecture.md) §4.1 (normalize) and prepares inputs for [chunking-embedding-architecture.md](../../../docs/chunking-embedding-architecture.md) §3.1.

## Behaviour

1. Reads `data/raw/<run_id>/manifest.json`, `amc.txt`, and each `*.html` from a successful scrape.
2. Parses Groww **`__NEXT_DATA__`** → `mfServerSideData` for structured fields.
3. Writes per-scheme **`*.txt`** (normalized plain text for chunking) under `data/normalized/<run_id>/`.
4. Writes **`scheme_facts.json`** (NAV, min SIP, AUM, expense ratio, Groww rating, risk label, etc.) per [rag-architecture §3.4](../../../docs/rag-architecture.md).
5. Writes **`normalize_manifest.json`** (paths, `normalized_text_hash` per file).

If `__NEXT_DATA__` is missing, falls back to **HTML → text** (BeautifulSoup) with sparse structured facts.

## CLI

```bash
# Latest scrape under data/raw
python3 -m ingest.phases.phase_4_1_normalize

# Specific run
python3 -m ingest.phases.phase_4_1_normalize --run-id 20260412T060804
```

## Environment

| Variable | Purpose |
|----------|---------|
| `INGEST_RAW_DIR` | Base dir for raw runs (default `data/raw`) |
| `INGEST_NORMALIZED_DIR` | Output base (default `data/normalized`) |
| `INGEST_REPO_ROOT` | Override repo root for default paths |

## Next phase

Chunk + embed: [phase_4_2_chunk_embedding](../phase_4_2_chunk_embedding/).
