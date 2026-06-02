"""CLI entry: python -m ingest.phases.phase_4_0_scheduler_scraping"""

from __future__ import annotations

import logging
import sys

from ingest.repo_dotenv import load_repo_dotenv
from ingest.phases.phase_4_0_scheduler_scraping.scraper import run_scrape


def main() -> int:
    load_repo_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        manifest = run_scrape()
    except Exception:
        logging.exception("Scrape run failed")
        return 1

    failed = [r for r in manifest.results if r.status != "ok"]
    if failed:
        logging.warning("%d URL(s) failed (see manifest)", len(failed))
        # Non-zero exit so CI surfaces partial failure
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
