# Runtime (query path)

Implements [docs/rag-architecture.md](../docs/rag-architecture.md) **§5–§9** query path.

| Folder | Role |
|--------|------|
| [`phase_5_retrieval/`](phase_5_retrieval/) | Embed query → Chroma → merge by `source_url` → citation |
| [`phase_6_generation/`](phase_6_generation/) | Context packaging → **Groq** → JSON answer → §7.2 validation |
| [`phase_7_safety/`](phase_7_safety/) | **§7.1** router + refusal, **§7.3** PII helpers; orchestrates 5→6 |
| [`phase_8_threads/`](phase_8_threads/) | **§8** SQLite thread/message store, last-N context, optional retrieval expansion → `answer()` |
| [`phase_9_api/`](phase_9_api/) | **§9** FastAPI HTTP API + static HTML/CSS/JS test UI |

**Single-shot CLI:** `python -m runtime.phase_7_safety "…"`. **Multi-turn:** `python -m runtime.phase_8_threads new-thread` then `say` / `history`. **HTTP API:** `python -m runtime.phase_9_api` (default `http://127.0.0.1:8765`). **Web UI:** Next.js app in [`web/`](../web/README.md) (`npm run dev`, set `NEXT_PUBLIC_API_URL` to the API). Use the repo **venv** and **`pip install -r requirements.txt`** so **`groq`** is installed (otherwise factual questions return **503** with a clear message). API smoke tests: `python -m unittest runtime.phase_9_api.test_api -v`. Ingest lives under [`ingest/`](../ingest/).
