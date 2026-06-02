"""Retrieval query expansion from recent user history (rag-architecture.md §8.2)."""

from __future__ import annotations

import re

from runtime.phase_8_threads.types import Message

_FOLLOWUP_START = re.compile(
    r"^(what about|and |also |how about|same |the exit|the sip|the nav|it |that |this )",
    re.IGNORECASE,
)


def expand_query_for_retrieval(
    current_user_text: str,
    history: list[Message],
    *,
    max_prior_user_utterances: int = 2,
    max_segment_chars: int = 500,
    short_followup_threshold: int = 120,
) -> str:
    """
    Optionally enrich the latest user message with prior **user** lines only (no assistant
    echo) to support short follow-ups like “What about exit load?” — capped length, no PII
    handling beyond truncation (§8.2).
    """
    text = current_user_text.strip()
    if not text:
        return text

    users = [
        m.content.strip()[:max_segment_chars]
        for m in history
        if m.role == "user" and m.content.strip()
    ]
    priors = users[-max_prior_user_utterances:] if max_prior_user_utterances > 0 else []
    if not priors:
        return text

    is_short = len(text) <= short_followup_threshold
    looks_followup = bool(_FOLLOWUP_START.search(text))
    if not (is_short or looks_followup):
        return text

    joined = " | ".join(priors)
    out = f"{joined} | Follow-up: {text}"
    return out[:3000]
