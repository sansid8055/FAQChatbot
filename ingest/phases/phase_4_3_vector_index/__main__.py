"""CLI: python -m ingest.phases.phase_4_3_vector_index"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from ingest.repo_dotenv import load_repo_dotenv
from ingest.phases.phase_4_3_vector_index import config
from ingest.phases.phase_4_3_vector_index.pipeline import discover_latest_chunked_run, run_chroma_index


def main() -> int:
    load_repo_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="Upsert chunk embeddings into Chroma (phase 4.3)")
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Chunked run directory under data/chunked (default: latest with embeddings)",
    )
    parser.add_argument(
        "--chunked-dir",
        type=Path,
        default=None,
        help="Override chunked base directory",
    )
    parser.add_argument(
        "--chroma-dir",
        type=Path,
        default=None,
        help="Override Chroma persist directory (default: data/chroma or INGEST_CHROMA_DIR)",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=None,
        help="Override url registry YAML (default: ingest/url_registry/urls.yaml)",
    )
    args = parser.parse_args()

    chunk_base = (args.chunked_dir or config.chunked_dir()).resolve()
    if args.run_id:
        run_dir = chunk_base / args.run_id
    else:
        found = discover_latest_chunked_run(chunk_base)
        if not found:
            logging.error("No chunked run with embeddings under %s", chunk_base)
            return 1
        run_dir = found
        logging.info("Using latest chunked run: %s", run_dir.name)

    try:
        run_chroma_index(
            run_dir,
            chroma_persist=args.chroma_dir,
            registry_path=args.registry,
        )
    except Exception:
        logging.exception("Chroma index failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
