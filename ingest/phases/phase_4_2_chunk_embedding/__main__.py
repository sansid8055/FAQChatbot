"""CLI: python -m ingest.phases.phase_4_2_chunk_embedding"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from ingest.repo_dotenv import load_repo_dotenv
from ingest.phases.phase_4_2_chunk_embedding import config
from ingest.phases.phase_4_2_chunk_embedding.pipeline import discover_latest_normalized_run, run_chunk_embed


def main() -> int:
    load_repo_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="Chunk + embed normalized corpus (phase 4.2)")
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Normalized run directory under data/normalized (default: latest)",
    )
    parser.add_argument(
        "--normalized-dir",
        type=Path,
        default=None,
        help="Override normalized base directory",
    )
    parser.add_argument(
        "--no-embed",
        action="store_true",
        help="Only write chunks.jsonl (skip local model inference)",
    )
    args = parser.parse_args()

    norm_base = (args.normalized_dir or config.normalized_dir()).resolve()
    if args.run_id:
        run_dir = norm_base / args.run_id
    else:
        found = discover_latest_normalized_run(norm_base)
        if not found:
            logging.error("No normalized run under %s", norm_base)
            return 1
        run_dir = found
        logging.info("Using latest normalized run: %s", run_dir.name)

    try:
        run_chunk_embed(run_dir, embed=not args.no_embed)
    except Exception:
        logging.exception("Chunk/embed failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
