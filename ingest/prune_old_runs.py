"""Remove past ingest run directories so only one run remains per stage.

Use after a successful full pipeline (same sequence as ``ingest.yml``): keeps the
latest chunked run id (which matches ``data/raw/<run_id>`` and ``data/normalized/<run_id>``
from that pipeline) and deletes sibling run directories under raw / normalized / chunked.

Optional: trim old ``data/logs/ingest-*.log`` files (newest N retained).

CLI: ``python -m ingest.prune_old_runs`` [--keep RUN_ID] [--dry-run] [--log-files N]
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
from pathlib import Path

from ingest.phases.phase_4_0_scheduler_scraping.config import raw_output_dir
from ingest.phases.phase_4_1_normalize.config import normalized_output_dir
from ingest.phases.phase_4_2_chunk_embedding.config import chunked_output_dir, repo_root
from ingest.phases.phase_4_3_vector_index.pipeline import discover_latest_chunked_run

logger = logging.getLogger(__name__)


def _is_raw_run_dir(p: Path) -> bool:
    return p.is_dir() and (p / "manifest.json").is_file()


def _is_normalized_run_dir(p: Path) -> bool:
    return p.is_dir() and (p / "normalize_manifest.json").is_file()


def _is_chunked_run_dir(p: Path) -> bool:
    return p.is_dir() and (p / "chunk_run_manifest.json").is_file()


def prune_run_directories(
    keep_run_id: str,
    *,
    dry_run: bool = False,
) -> dict[str, list[str]]:
    """Delete all run dirs except ``keep_run_id`` under raw, normalized, chunked."""
    removed: dict[str, list[str]] = {"raw": [], "normalized": [], "chunked": []}
    bases = [
        ("raw", raw_output_dir(), _is_raw_run_dir),
        ("normalized", normalized_output_dir(), _is_normalized_run_dir),
        ("chunked", chunked_output_dir(), _is_chunked_run_dir),
    ]
    for key, base, pred in bases:
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if not pred(child):
                continue
            if child.name == keep_run_id:
                continue
            removed[key].append(child.name)
            if dry_run:
                logger.info("DRY-RUN would remove %s", child)
            else:
                shutil.rmtree(child)
                logger.info("Removed %s %s", key, child)
    return removed


def prune_ingest_logs(*, keep_files: int, dry_run: bool = False) -> list[str]:
    """Keep the ``keep_files`` newest ``ingest-*.log`` under ``data/logs``; delete the rest."""
    if keep_files < 1:
        return []
    logs_dir = repo_root() / "data" / "logs"
    if not logs_dir.is_dir():
        return []
    candidates = sorted(
        (p for p in logs_dir.glob("ingest-*.log") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    to_delete = candidates[keep_files:]
    names: list[str] = []
    for p in to_delete:
        names.append(p.name)
        if dry_run:
            logger.info("DRY-RUN would remove log %s", p)
        else:
            p.unlink()
            logger.info("Removed log %s", p)
    return names


def resolve_keep_run_id(explicit: str | None) -> str:
    if explicit:
        return explicit
    chunk_base = chunked_output_dir()
    latest = discover_latest_chunked_run(chunk_base)
    if not latest:
        raise FileNotFoundError(
            f"No chunked run with embeddings under {chunk_base} — run phase 4.2 first."
        )
    return latest.name


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--keep",
        metavar="RUN_ID",
        help="Run directory name to keep (default: latest chunked run with embeddings)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions only; do not delete",
    )
    ap.add_argument(
        "--log-files",
        type=int,
        metavar="N",
        default=20,
        help="Retain N newest ingest-*.log files under data/logs (0 = skip log pruning)",
    )
    args = ap.parse_args()
    if os.environ.get("INGEST_PRUNE_SKIP", "").strip().lower() in ("1", "true", "yes"):
        logger.info("INGEST_PRUNE_SKIP set — skipping prune")
        return

    keep = resolve_keep_run_id(args.keep)
    logger.info("Keeping ingest run_id=%s", keep)

    summary = prune_run_directories(keep, dry_run=args.dry_run)
    for k, v in summary.items():
        if v:
            logger.info("Pruned %s: %d dir(s) %s", k, len(v), v)

    if args.log_files > 0:
        logs_removed = prune_ingest_logs(keep_files=args.log_files, dry_run=args.dry_run)
        if logs_removed:
            logger.info("Pruned %d ingest log file(s)", len(logs_removed))


if __name__ == "__main__":
    main()
