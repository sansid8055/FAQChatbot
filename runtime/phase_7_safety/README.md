# Phase 7 — Refusal & safety

Implements [docs/rag-architecture.md](../../../docs/rag-architecture.md) **§7**:

| Piece | Module |
|-------|--------|
| **§7.1** Pre-retrieval router | `router.py` — blocks advisory / comparative / “should I” style queries |
| **§7.1** Refusal response | `refusal.py` — polite copy + **one** educational URL (default AMFI investor education) |
| **§7.2** Post-generation validation | Still enforced inside **phase 6** `generate()`; `post_validate.py` re-exports helpers |
| **§7.3** Privacy helpers | `privacy.py` — PAN/Aadhaar-like/email/phone heuristics, `redact_for_logs()` |

## Run (recommended entrypoint)

```bash
python -m runtime.phase_7_safety "What is the NAV of HDFC Equity?"
python -m runtime.phase_7_safety "Should I buy HDFC Mid Cap?"   # → refusal, no Chroma/Groq
python -m runtime.phase_7_safety --route-only "which fund is better?"
python -m runtime.phase_7_safety --json "Your question"
```

## API

```python
from runtime.phase_7_safety import answer, route_query, redact_for_logs

g = answer("User question")  # GenerationResult (same type as phase 6)
d = route_query("...")       # RouteDecision
safe_line = redact_for_logs(raw_for_log)
```

## Environment

| Variable | Purpose |
|----------|---------|
| `EDUCATIONAL_URL` | §7.1 link (default AMFI investor education page) |
| Same as phases 5–6 | `INGEST_CHROMA_*`, `GROQ_*`, `INGEST_REGISTRY_PATH`, … |

**§7.3 default:** queries that look like they contain PAN, 12-digit blocks, email, or phone are **not** sent to retrieval/LLM unless you pass `block_on_pii_in_query=False` or CLI `--allow-pii-queries` (testing only).
