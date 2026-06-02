"""Query preprocessing and scheme resolution (rag-architecture.md §5.1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


def normalize_for_match(text: str) -> str:
    """Lowercase and collapse whitespace for dictionary / substring checks."""
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t


def resolve_scheme_filter(query: str, registry_path: Path) -> str | None:
    """
    If the query clearly names a single allowlisted scheme, return ``scheme_id`` for Chroma ``where``.

    Uses URL slug and scheme name heuristics; returns ``None`` if ambiguous or unknown.
    """
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    entries: list[Any] = raw.get("entries") or []
    rows: list[dict[str, str]] = []
    for row in entries:
        if not isinstance(row, dict):
            continue
        sid = row.get("scheme_id")
        url = row.get("url", "")
        name = row.get("scheme_name", "")
        if isinstance(sid, str) and sid.strip():
            slug = ""
            if isinstance(url, str) and url:
                slug = url.rstrip("/").split("/")[-1].lower()
            rows.append(
                {
                    "scheme_id": sid.strip(),
                    "scheme_name": name.strip() if isinstance(name, str) else "",
                    "slug": slug,
                }
            )

    qn = normalize_for_match(query)
    qn_space = qn.replace("-", " ")

    # 1) Groww URL slug as a phrase (hyphens → spaces). One clear slug wins; avoids
    #    false multi-matches from the token heuristic (many schemes share hdfc/fund/direct/growth).
    slug_hits: list[str] = []
    for r in rows:
        slug = r["slug"]
        sid = r["scheme_id"]
        if slug:
            sp = slug.replace("-", " ").lower()
            if sp in qn_space:
                slug_hits.append(sid)
    seen_slug: set[str] = set()
    slug_uniq: list[str] = []
    for s in slug_hits:
        if s not in seen_slug:
            seen_slug.add(s)
            slug_uniq.append(s)
    if len(slug_uniq) == 1:
        return slug_uniq[0]
    if len(slug_uniq) > 1:
        return None

    # 2) Token / name heuristics when no slug phrase matched
    matches: list[str] = []

    for r in rows:
        sid = r["scheme_id"]
        name = r["scheme_name"].lower()

        parts = [p for p in sid.split("-") if len(p) > 2]
        if len(parts) >= 2:
            need = min(3, len(parts))
            hit_c = sum(1 for p in parts if p in qn)
            if hit_c >= need:
                matches.append(sid)
                continue

        if len(name) > 15 and name in qn:
            matches.append(sid)

    seen: set[str] = set()
    uniq: list[str] = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            uniq.append(m)

    if len(uniq) == 1:
        return uniq[0]
    return None
