# Phase 6 — Generation (Groq)

Implements [docs/rag-architecture.md](../../../docs/rag-architecture.md) **§6** (prompting, context packaging, output contract) and **§7.2** post-generation validation (sentence count, allowlisted URL, forbidden phrases). The LLM is **[Groq](https://groq.com/)** (fast OpenAI-compatible chat API).

## Setup

1. Copy [`.env.example`](../../../.env.example) → `.env` and set **`GROQ_API_KEY`** (from [Groq console](https://console.groq.com/)).
2. Optional: **`GROQ_MODEL`** (default `llama-3.1-8b-instant`), **`GROQ_TEMPERATURE`** (default `0.2`).
3. Chroma + retrieval paths same as phase 5 / 4.3 (`INGEST_CHROMA_DIR`, `INGEST_CHROMA_COLLECTION`, etc.).

## Run (retrieve + generate)

```bash
python -m runtime.phase_6_generation "What is the expense ratio for HDFC Mid Cap?"
python -m runtime.phase_6_generation --json "Your question"
```

## API

```python
from runtime.phase_5_retrieval import retrieve
from runtime.phase_6_generation import generate, GenerationResult

r = retrieve("Your question")
g: GenerationResult = generate(r)
print(g.user_visible)   # body + blank line + URL + blank line + footer
```

## Output policy (§6.2)

- **Body:** ≤3 sentences, no URL inside body (validated).
- **Citation:** Exactly one allowlisted HTTPS URL, forced to match phase 5 `citation_url` when validation passes.
- **Footer:** `Last updated from sources: <YYYY-MM-DD>` from the **cited** chunk’s `fetched_at` (same policy as architecture: cited source date).

If Groq fails or JSON/validation fails twice, a **templated safe reply** is returned with the same citation URL and footer (§7.2 fallback).
