"""Defaults for phase 4.0 scraping (override via environment variables)."""

from __future__ import annotations

import os
from pathlib import Path

# Stable UA identifying the project (do not impersonate browsers).
DEFAULT_USER_AGENT = (
    "MF-FAQ-Assistant-Ingest/1.0 "
    "(+https://github.com/; contact: ops@example.invalid)"
)

# Seconds between HTTP GETs to the same host (rate limiting).
DEFAULT_RATE_LIMIT_SECONDS = 1.5

# Per-request timeout (connect + read).
DEFAULT_TIMEOUT_SECONDS = 30.0

# Repo-root-relative default paths (resolved at runtime from cwd).
# ingest/phases/phase_4_0_scheduler_scraping/config.py -> repo root is parents[3]
_DEFAULT_ROOT = Path(__file__).resolve().parents[3]


def registry_path() -> Path:
    p = os.environ.get("INGEST_REGISTRY_PATH")
    if p:
        return Path(p).expanduser().resolve()
    return _DEFAULT_ROOT / "ingest" / "url_registry" / "urls.yaml"


def raw_output_dir() -> Path:
    p = os.environ.get("INGEST_RAW_DIR")
    if p:
        return Path(p).expanduser().resolve()
    return _DEFAULT_ROOT / "data" / "raw"


def user_agent() -> str:
    return os.environ.get("INGEST_USER_AGENT", DEFAULT_USER_AGENT).strip() or DEFAULT_USER_AGENT


def rate_limit_seconds() -> float:
    raw = os.environ.get("INGEST_RATE_LIMIT_SECONDS", "").strip()
    if not raw:
        return DEFAULT_RATE_LIMIT_SECONDS
    return float(raw)


def timeout_seconds() -> float:
    raw = os.environ.get("INGEST_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return DEFAULT_TIMEOUT_SECONDS
    return float(raw)
