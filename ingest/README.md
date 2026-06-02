# Ingestion pipeline (phased)

Aligned with [docs/rag-architecture.md](../docs/rag-architecture.md). **Query-time retrieval (§5)** lives in [`runtime/phase_5_retrieval/`](../runtime/phase_5_retrieval/); **generation (§6, Groq)** in [`runtime/phase_6_generation/`](../runtime/phase_6_generation/); **safety router (§7)** in [`runtime/phase_7_safety/`](../runtime/phase_7_safety/) (`python -m runtime.phase_7_safety` recommended).

**Local config:** copy [`.env.example`](../.env.example) to **`.env`** in the repo root if you need overrides (optional `INGEST_*`, `GROQ_API_KEY` for runtime). All phase `python -m ingest...` entrypoints load `.env` automatically. **Do not commit `.env`.**

| Folder | Phase | Status |
|--------|--------|--------|
| [`url_registry/`](url_registry/) | §4.1 URL registry | **Active** — YAML allowlist |
| [`phases/phase_4_0_scheduler_scraping/`](phases/phase_4_0_scheduler_scraping/) | §4.0 Scheduler + scraping | **Implemented** |
| [`phases/phase_4_1_normalize/`](phases/phase_4_1_normalize/) | §4.1 Normalize HTML | **Implemented** |
| [`phases/phase_4_2_chunk_embedding/`](phases/phase_4_2_chunk_embedding/) | §4.1 Chunk + embed | **Implemented** |
| [`phases/phase_4_3_vector_index/`](phases/phase_4_3_vector_index/) | §4.3 Chroma vector index | **Implemented** — see [rag-architecture.md](../docs/rag-architecture.md) §4.3 |

## Local scheduler (full pipeline + log)

To mirror [.github/workflows/ingest.yml](../.github/workflows/ingest.yml) on your machine (all phases in order) and capture **stdout/stderr** to a timestamped log under `data/logs/`:

```bash
./scripts/run-ingest-local.sh
```

Optional: pass a custom log path as the first argument:

```bash
./scripts/run-ingest-local.sh /tmp/my-ingest.log
```

The script uses `.venv/bin/python` when present, otherwise `python3`. It sets `HF_HOME` to `.cache/huggingface` under the repo when unset (same idea as CI). Log lines are prefixed with UTC timestamps for each phase boundary.

After a successful **4.3**, the script runs **`python -m ingest.prune_old_runs`** so only the **latest** `run_id` remains under `data/raw/`, `data/normalized/`, and `data/chunked/` (older scrape runs are removed). It also keeps the **20** newest `data/logs/ingest-*.log` files and deletes older logs. Set **`INGEST_PRUNE_SKIP=1`** (or `true`/`yes`) to skip that step.

### Prune only (manual)

```bash
python3 -m ingest.prune_old_runs
python3 -m ingest.prune_old_runs --dry-run
python3 -m ingest.prune_old_runs --keep 20260415T150337
python3 -m ingest.prune_old_runs --log-files 0   # do not prune ingest logs
```

**Chroma:** phase **4.3** upserts the current run, then **deletes** any collection IDs that are not in that run (removes stale vectors when chunk counts or registry entries change). The persist directory is reused; it is not deleted wholesale.

## Run scrape locally

From the repository root:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m ingest.phases.phase_4_0_scheduler_scraping
```

Outputs under `data/raw/<run_id>/`: one `.html` per successful URL, `manifest.json`, and `amc.txt`.

### Run normalize (phase 4.1)

```bash
python3 -m ingest.phases.phase_4_1_normalize
# or: python3 -m ingest.phases.phase_4_1_normalize --run-id <run_id>
```

Outputs under `data/normalized/<run_id>/`: one `.txt` per scheme, `scheme_facts.json`, `normalize_manifest.json`.

### Chunk + embed (phase 4.2)

```bash
python3 -m ingest.phases.phase_4_2_chunk_embedding
# Add --no-embed to skip local model inference
```

Outputs under `data/chunked/<run_id>/`: `chunks.jsonl`, optional `embeddings.jsonl`, `chunk_run_manifest.json`.

### Chroma index (phase 4.3)

```bash
python3 -m ingest.phases.phase_4_3_vector_index
# or: python3 -m ingest.phases.phase_4_3_vector_index --run-id <run_id>
```

Writes vectors to **on-disk Chroma** under `INGEST_CHROMA_DIR` (default `data/chroma`) and always writes `chroma_index_manifest.json` next to the chunked run. See [phase_4_3_vector_index/README.md](phases/phase_4_3_vector_index/README.md).

### Environment variables

| Variable | Purpose |
|----------|---------|
| `INGEST_REGISTRY_PATH` | Path to `urls.yaml` (default: `ingest/url_registry/urls.yaml`) |
| `INGEST_RAW_DIR` | Base directory for raw HTML (default: `data/raw`) |
| `INGEST_USER_AGENT` | HTTP User-Agent string |
| `INGEST_RATE_LIMIT_SECONDS` | Delay between requests (default `1.5`) |
| `INGEST_TIMEOUT_SECONDS` | Per-request timeout (default `30`) |
| `INGEST_NORMALIZED_DIR` | Phase 4.1 output base (default `data/normalized`) |
| `INGEST_REPO_ROOT` | Repo root for default `data/*` paths |
| `INGEST_CHUNKED_DIR` | Phase 4.2 output base (default `data/chunked`) |
| `INGEST_CHROMA_DIR` | Chroma persist directory (default `data/chroma`) |
| `INGEST_CHROMA_COLLECTION` | Collection name (default `mf_faq_chunks`) |
| `INGEST_CHROMA_UPSERT_BATCH` | Upsert batch size for phase 4.3 (default `64`) |
| `HF_HOME` | Hugging Face model cache dir (optional) |
| `INGEST_PRUNE_SKIP` | If `1`/`true`/`yes`, skip prune in `run-ingest-local.sh` and make `python -m ingest.prune_old_runs` a no-op |

## Scheduler (GitHub Actions)

Workflow: [.github/workflows/ingest.yml](../.github/workflows/ingest.yml) — **Daily at 09:15 IST** (`cron: 45 3 * * *` UTC; India has no DST). You can also run it manually via **Actions → Daily ingest (09:15 IST) → Run workflow**.

Each run executes **in order** on a clean checkout (the same `run_id` flows through all stages):

1. **Phase 4.0** — Scrape allowlisted URLs → `data/raw/<run_id>/`
2. **Phase 4.1** — Normalize HTML → `data/normalized/<run_id>/`
3. **Phase 4.2** — Chunk + **local** BGE embeddings → `data/chunked/<run_id>/` (`chunks.jsonl`, `embeddings.jsonl`)
4. **Phase 4.3** — **Upsert** embeddings + metadata to **local Chroma** (`data/chroma/` by default)

**Secrets (repository):** Optional **`INGEST_USER_AGENT`** for scraping (otherwise defaults from `config.py`). The workflow uploads **`data/chroma/`** as an artifact for operators or downstream deploy steps.
