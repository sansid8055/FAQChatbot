"""CLI: full RAG slice — phase 5 retrieve + phase 6 Groq generate."""

from __future__ import annotations

import argparse
import json
import logging
import sys

from ingest.repo_dotenv import load_repo_dotenv

from runtime.phase_5_retrieval.pipeline import retrieve
from runtime.phase_6_generation.pipeline import generate


def main() -> int:
    load_repo_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Phase 6 — retrieve (§5) + Groq generation (§6)"
    )
    parser.add_argument("query", nargs="?", default="", help="User question")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON instead of plain user_visible",
    )
    args = parser.parse_args()
    q = (args.query or "").strip()
    if not q:
        parser.error(
            'Pass a query, e.g. python -m runtime.phase_6_generation "What is the expense ratio?"'
        )

    try:
        r = retrieve(q)
        g = generate(r)
    except Exception:
        logging.exception("Pipeline failed")
        return 1

    if args.json:
        out = {
            "body": g.body,
            "citation_url": g.citation_url,
            "footer": g.footer,
            "user_visible": g.user_visible,
            "model": g.model,
            "validation_ok": g.validation_ok,
            "fallback_used": g.fallback_used,
            "advisory_refusal": g.advisory_refusal,
            "router_reason": g.router_reason,
        }
        print(json.dumps(out, indent=2))
    else:
        print(g.user_visible)
    return 0


if __name__ == "__main__":
    sys.exit(main())
