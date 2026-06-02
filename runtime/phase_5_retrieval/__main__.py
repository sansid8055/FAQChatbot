"""CLI: python -m runtime.phase_5_retrieval \"your question\""""

from __future__ import annotations

import argparse
import json
import logging
import sys

from ingest.repo_dotenv import load_repo_dotenv

from runtime.phase_5_retrieval.pipeline import retrieve
from runtime.phase_5_retrieval.types import MergedContext, RetrievalResult


def _result_to_jsonable(r: RetrievalResult) -> dict:
    def ctx_dict(c: MergedContext) -> dict:
        return {
            "source_url": c.source_url,
            "distance": c.distance,
            "scheme_id": c.scheme_id,
            "scheme_name": c.scheme_name,
            "fetched_at": c.fetched_at,
            "chunk_ids": c.chunk_ids,
            "text_preview": c.text[:500] + ("…" if len(c.text) > 500 else ""),
        }

    return {
        "query": r.query,
        "scheme_filter": r.scheme_filter,
        "citation_url": r.citation_url,
        "citation_fetched_at": r.citation_fetched_at,
        "citation_scheme_id": r.citation_scheme_id,
        "contexts": [ctx_dict(c) for c in r.contexts],
    }


def main() -> int:
    load_repo_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="Phase 5 — retrieve from Chroma (rag §5)")
    parser.add_argument("query", nargs="?", default="", help="User question")
    args = parser.parse_args()
    q = (args.query or "").strip()
    if not q:
        parser.error(
            'Pass a query string, e.g. python -m runtime.phase_5_retrieval "What is the expense ratio?"'
        )

    try:
        result = retrieve(q)
    except Exception:
        logging.exception("Retrieval failed")
        return 1

    print(json.dumps(_result_to_jsonable(result), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
