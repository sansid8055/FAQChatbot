"""Paths for phase 4.1 normalize (override via environment variables)."""

from __future__ import annotations

import os
from pathlib import Path

# ingest/phases/phase_4_1_normalize/config.py -> repo root is parents[3]
_DEFAULT_ROOT = Path(__file__).resolve().parents[3]


def repo_root() -> Path:
    p = os.environ.get("INGEST_REPO_ROOT")
    if p:
        return Path(p).expanduser().resolve()
    return _DEFAULT_ROOT


def raw_output_dir() -> Path:
    p = os.environ.get("INGEST_RAW_DIR")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "data" / "raw"


def normalized_output_dir() -> Path:
    p = os.environ.get("INGEST_NORMALIZED_DIR")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "data" / "normalized"
