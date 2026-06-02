"""Generation layer types (rag-architecture.md §6)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Assistant-facing reply after §6 (+ §7.2 validation) or §7.1 refusal."""

    body: str
    citation_url: str
    footer: str
    """Full message for UI: body, link, footer (architecture §6.2)."""

    user_visible: str
    model: str
    validation_ok: bool
    fallback_used: bool
    raw_model_response: str | None = None
    advisory_refusal: bool = False
    router_reason: str | None = None
