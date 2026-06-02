"""Extra post-generation checks aligned with rag-architecture.md §7.2."""

from __future__ import annotations

from runtime.phase_6_generation.validate_output import (
    count_urls,
    validate_generation,
)

# Re-export for callers that anchor on phase 7
validate_generation_output = validate_generation


def user_visible_has_single_http_url(user_visible: str) -> bool:
    """§7.2 — exactly one HTTP(S) URL in the full assistant-facing string."""
    n = count_urls(user_visible or "")
    return n == 1
