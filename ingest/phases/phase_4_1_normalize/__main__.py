"""CLI: python -m ingest.phases.phase_4_1_normalize"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from ingest.repo_dotenv import load_repo_dotenv
from ingest.phases.phase_4_1_normalize import config
from ingest.phases.phase_4_1_normalize.normalize import discover_latest_raw_run, run_normalize


def main() -> int:
    load_repo_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="Normalize raw Groww HTML (phase 4.1)")
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Scrape run directory name under data/raw (default: latest with manifest.json)",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Override data/raw base (default from INGEST_RAW_DIR or repo data/raw)",
    )
    args = parser.parse_args()

    raw_base = (args.raw_dir or config.raw_output_dir()).resolve()
    if args.run_id:
        raw_run = raw_base / args.run_id
    else:
        found = discover_latest_raw_run(raw_base)
        if not found:
            logging.error("No scrape run found under %s (need manifest.json)", raw_base)
            return 1
        raw_run = found
        logging.info("Using latest raw run: %s", raw_run.name)

    try:
        run_normalize(raw_run)
    except Exception:
        logging.exception("Normalize failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
