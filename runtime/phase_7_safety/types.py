"""Router / safety types (rag-architecture.md §7)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RouteDecision:
    """Result of the pre-retrieval router (§7.1)."""

    allow_retrieval: bool
    """If False, skip Chroma + Groq; return educational refusal instead."""

    advisory: bool
    matched_rule: str | None
    """Stable id of the first rule that fired, for logs/metrics."""
