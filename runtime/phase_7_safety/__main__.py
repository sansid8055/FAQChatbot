"""CLI: phase 7 full path — router + optional PII gate + retrieve + Groq."""

from __future__ import annotations

import argparse
import json
import logging
import sys

from ingest.repo_dotenv import load_repo_dotenv

from runtime.phase_7_safety.pipeline import answer
from runtime.phase_7_safety.router import route_query


def main() -> int:
    load_repo_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Phase 7 — safety router + RAG (rag-architecture.md §7)"
    )
    parser.add_argument("query", nargs="?", default="", help="User question")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Structured JSON output",
    )
    parser.add_argument(
        "--route-only",
        action="store_true",
        help="Print router decision JSON only (no retrieval/LLM)",
    )
    parser.add_argument(
        "--allow-pii-queries",
        action="store_true",
        help="Disable §7.3 heuristic block on PAN/Aadhaar/email/phone in the query",
    )
    args = parser.parse_args()
    q = (args.query or "").strip()
    if not q:
        parser.error('Pass a query, e.g. python -m runtime.phase_7_safety "What is the NAV?"')

    if args.route_only:
        d = route_query(q)
        print(
            json.dumps(
                {
                    "allow_retrieval": d.allow_retrieval,
                    "advisory": d.advisory,
                    "matched_rule": d.matched_rule,
                },
                indent=2,
            )
        )
        return 0

    try:
        g = answer(
            q,
            block_on_pii_in_query=not args.allow_pii_queries,
        )
    except Exception:
        logging.exception("Pipeline failed")
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "body": g.body,
                    "citation_url": g.citation_url,
                    "footer": g.footer,
                    "user_visible": g.user_visible,
                    "model": g.model,
                    "validation_ok": g.validation_ok,
                    "fallback_used": g.fallback_used,
                    "advisory_refusal": g.advisory_refusal,
                    "router_reason": g.router_reason,
                },
                indent=2,
            )
        )
    else:
        print(g.user_visible)
    return 0


if __name__ == "__main__":
    sys.exit(main())
