# Mutual Fund FAQ Assistant (ingest)

Facts-only RAG assistant — see [docs/problemStatement.md](docs/problemStatement.md) and [docs/rag-architecture.md](docs/rag-architecture.md).

## Ingestion (implemented: phase 4.0)

- **URL registry:** [ingest/url_registry/urls.yaml](ingest/url_registry/urls.yaml)
- **Scraping service:** [ingest/phases/phase_4_0_scheduler_scraping/](ingest/phases/phase_4_0_scheduler_scraping/)
- **Normalize (4.1):** [ingest/phases/phase_4_1_normalize/](ingest/phases/phase_4_1_normalize/) — `__NEXT_DATA__` → `.txt` + `scheme_facts.json`
- **Chunk + embed (4.2):** [ingest/phases/phase_4_2_chunk_embedding/](ingest/phases/phase_4_2_chunk_embedding/) — WordPiece packing + local `bge-small-en-v1.5` embeddings (384-dim)
- **Chroma index (4.3):** [ingest/phases/phase_4_3_vector_index/](ingest/phases/phase_4_3_vector_index/) — on-disk **`PersistentClient`** under `data/chroma/` (same store phase 5 reads at query time)
- **Scheduler:** [.github/workflows/ingest.yml](.github/workflows/ingest.yml) — daily **09:15 IST** (`45 3 * * *` UTC) + manual run; full pipeline **scrape → normalize → chunk → embed → local Chroma**

### Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: optional INGEST_CHROMA_DIR / INGEST_CHROMA_COLLECTION; GROQ_API_KEY for runtime LLM
python -m ingest.phases.phase_4_0_scheduler_scraping
```

Ingest CLIs load the repo-root **`.env`** automatically (via `python-dotenv`). **`.env` is gitignored**; only [`.env.example`](.env.example) is committed. Phase **6** needs **`GROQ_API_KEY`** for LLM replies; phase **7** adds the safety router (see [runtime/phase_7_safety/](runtime/phase_7_safety/) — run `python -m runtime.phase_7_safety "…"` for the full guarded path). Phase **9** serves the HTTP API (`python -m runtime.phase_9_api`); the chat UI is the **Next.js** app in [web/](web/) — see [web/README.md](web/README.md) (`npm run dev` with `NEXT_PUBLIC_API_URL` pointing at the API, e.g. `http://127.0.0.1:8765`).

More detail: [ingest/README.md](ingest/README.md).

## Phased layout

| Phase | Path |
|-------|------|
| 4.0 Scheduler + scraping | `ingest/phases/phase_4_0_scheduler_scraping/` |
| 4.1 Normalize | `ingest/phases/phase_4_1_normalize/` |
| 4.2 Chunk + embedding | `ingest/phases/phase_4_2_chunk_embedding/` |
| 4.3 Vector index | `ingest/phases/phase_4_3_vector_index/` |
| **5 Retrieval** (query-time) | [`runtime/phase_5_retrieval/`](runtime/phase_5_retrieval/) — [rag §5](docs/rag-architecture.md#5-retrieval-layer) |
| **6 Generation** (Groq) | [`runtime/phase_6_generation/`](runtime/phase_6_generation/) — [rag §6](docs/rag-architecture.md#6-generation-layer) |
| **7 Safety** | [`runtime/phase_7_safety/`](runtime/phase_7_safety/) — [rag §7](docs/rag-architecture.md#7-refusal--safety-layer) |
| **8 Threads** | [`runtime/phase_8_threads/`](runtime/phase_8_threads/) — [rag §8](docs/rag-architecture.md#8-multi-thread-chat-architecture) |
| **9 API + test UI** | [`runtime/phase_9_api/`](runtime/phase_9_api/) — [rag §9](docs/rag-architecture.md#9-application--api-layer-suggested) |
