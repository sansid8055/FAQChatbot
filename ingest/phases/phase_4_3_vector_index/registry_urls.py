"""Load allowlisted scheme_ids and URLs from ingest/url_registry/urls.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_allowlist(registry_path: Path) -> tuple[set[str], set[str]]:
    """Return (scheme_ids, source_urls) from the registry file."""
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "entries" not in raw:
        raise ValueError(f"Invalid registry YAML: {registry_path}")

    entries: list[Any] = raw.get("entries") or []
    scheme_ids: set[str] = set()
    urls: set[str] = set()
    for row in entries:
        if not isinstance(row, dict):
            continue
        sid = row.get("scheme_id")
        url = row.get("url")
        if isinstance(sid, str) and sid.strip():
            scheme_ids.add(sid.strip())
        if isinstance(url, str) and url.strip():
            urls.add(url.strip())
    return scheme_ids, urls
