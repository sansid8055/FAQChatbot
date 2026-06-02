"""Post-generation checks (rag-architecture.md §7.2, invoked from phase 6 pipeline)."""

from __future__ import annotations

import re

# Forbidden advice / hype patterns (case-insensitive)
FORBIDDEN_PATTERNS = re.compile(
    r"\b("
    r"you should invest|you should buy|invest in this|better than|outperform|"
    r"guarantee|best fund|which fund should|recommend (a |the )?fund|"
    r"i recommend|we recommend"
    r")\b",
    re.I,
)

_URL_RE = re.compile(r"https?://[^\s\)>\]\"']+")


def sentence_count_heuristic(text: str) -> int:
    """Rough sentence count for §7.2 (body only, no URLs)."""
    t = text.strip()
    if not t:
        return 0
    parts = re.split(r"(?<=[.!?])\s+", t)
    return len([p for p in parts if p.strip()])


def count_urls(text: str) -> int:
    return len(_URL_RE.findall(text))


def validate_generation(
    *,
    body: str,
    citation_url: str,
    footer: str,
    required_citation: str,
    required_footer_prefix: str,
    allowlisted_urls: frozenset[str],
) -> tuple[bool, str]:
    """Return (ok, reason)."""
    if FORBIDDEN_PATTERNS.search(body or ""):
        return False, "forbidden_phrase_in_body"
    if sentence_count_heuristic(body or "") > 3:
        return False, "body_too_many_sentences"
    if count_urls(body or "") > 0:
        return False, "url_in_body"
    if not citation_url or citation_url.strip() != required_citation.strip():
        return False, "citation_mismatch"
    if citation_url not in allowlisted_urls:
        return False, "citation_not_allowlisted"
    if not citation_url.startswith("http://") and not citation_url.startswith("https://"):
        return False, "citation_not_url"
    fp = required_footer_prefix.strip()
    if not (footer or "").strip().startswith(fp):
        return False, "footer_mismatch"
    return True, ""
