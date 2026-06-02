"""Allowlisted URLs from the ingest registry (§6.2 / §7.2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_allowlisted_urls(registry_path: Path) -> frozenset[str]:
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return frozenset()
    out: set[str] = set()
    for row in raw.get("entries") or []:
        if isinstance(row, dict):
            u = row.get("url")
            if isinstance(u, str) and u.strip():
                out.add(u.strip())
    return frozenset(out)
