"""Phase 7 orchestration: router → (refusal | retrieve → generate) (rag-architecture.md §7)."""

from __future__ import annotations

import logging
from pathlib import Path

from runtime.phase_6_generation.types import GenerationResult
from runtime.phase_7_safety.privacy import user_message_looks_sensitive
from runtime.phase_7_safety.refusal import educational_refusal
from runtime.phase_7_safety.router import route_query

logger = logging.getLogger(__name__)


def answer(
    query: str,
    *,
    registry_path: Path | None = None,
    block_on_pii_in_query: bool = True,
) -> GenerationResult:
    """
    Full safe path: §7.1 router → optional §7.3 PII gate → §5 retrieve → §6 generate.

    If ``block_on_pii_in_query`` and the message looks like it contains PAN/Aadhaar/email/phone,
    return an educational-style refusal (no retrieval) to avoid processing identifiers.
    """
    rd = route_query(query)
    if not rd.allow_retrieval:
        logger.info("Router blocked retrieval: %s", rd.matched_rule)
        return educational_refusal(router_rule=rd.matched_rule)

    if block_on_pii_in_query and user_message_looks_sensitive(query):
        logger.info("PII heuristic blocked query processing")
        return educational_refusal(router_rule="pii_heuristic")

    from runtime.phase_5_retrieval.pipeline import retrieve
    from runtime.phase_6_generation.pipeline import generate

    r = retrieve(query, registry_path=registry_path)
    return generate(r, registry_path=registry_path)
