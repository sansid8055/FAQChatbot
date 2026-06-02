"""Phase 4.1: normalize HTML → plain text + structured scheme facts."""

from ingest.phases.phase_4_1_normalize.normalize import (
    discover_latest_raw_run,
    run_normalize,
)

__all__ = ["discover_latest_raw_run", "run_normalize"]
