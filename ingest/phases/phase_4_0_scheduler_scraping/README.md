# Phase 4.0 — Scheduler & scraping service

Implements [docs/rag-architecture.md](../../../docs/rag-architecture.md) §4.0.

## Responsibilities

- Read **`ingest/url_registry/urls.yaml`** (allowlist only).
- For each entry: check `robots.txt`, **GET** the URL with a stable User-Agent, **rate-limit** between requests, write **raw HTML** to `data/raw/<run_id>/<scheme_id>.html`.
- Write **`manifest.json`** per run (per-URL status, `content_hash`, errors).
- Exit **2** if any URL failed (so CI shows failure while still processing all URLs).

## Entry points

- **Local / CI:** `python -m ingest.phases.phase_4_0_scheduler_scraping`
- **Programmatic:** `from ingest.phases.phase_4_0_scheduler_scraping import run_scrape` then `run_scrape()`

## Next phase

Normalized HTML is consumed by [phase_4_1_normalize](../phase_4_1_normalize/) (to be implemented).
