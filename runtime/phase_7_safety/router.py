"""Rule-based query router for advisory / comparative intent (rag-architecture.md §7.1)."""

from __future__ import annotations

import re

from runtime.phase_7_safety.types import RouteDecision

# (rule_id, pattern) — first match wins. Tuned to reduce false positives on factual FAQs.
_ADVISORY_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "should_i_invest",
        re.compile(
            r"\bshould i\b.*\b(buy|invest|put|sip|lump\s*sum|allocate)\b",
            re.I | re.DOTALL,
        ),
    ),
    (
        "which_better",
        re.compile(
            r"\bwhich\b.*\b(fund|scheme)s?\b.*\b(better|best|prefer|choose between)\b|\b"
            r"which\b.*\b(better|best)\b.*\b(fund|scheme)\b",
            re.I | re.DOTALL,
        ),
    ),
    (
        "best_fund_to",
        re.compile(
            r"\b(?:the\s+)?best\s+fund(s)?\s+(?:to|for)\s+(?:buy|invest|me|you)\b|\b"
            r"best\s+mutual\s+fund\b.*\b(invest|buy)\b",
            re.I,
        ),
    ),
    (
        "recommend_fund",
        re.compile(
            r"\b(recommend|suggest)\s+(me\s+)?(a\s+)?(fund|scheme|investment|portfolio)\b|\b"
            r"\bwhich\s+one\s+should\s+i\b",
            re.I,
        ),
    ),
    (
        "ranking",
        re.compile(
            r"\btop\s+\d+\s+funds?\b|\bcompare\s+(these\s+)?funds?\b|\boutperform\b|\b"
            r"beat\s+the\s+market\b",
            re.I,
        ),
    ),
    (
        "personal_situation",
        re.compile(
            r"\bi\s+am\s+\d{2}\b.*\b(invest|retir|save|fund)\b|\b"
            r"my\s+(age|situation|portfolio)\b.*\b(should|invest|fund)\b|\b"
            r"for\s+my\s+child\b.*\b(which|best|should)\b",
            re.I,
        ),
    ),
    (
        "guarantee_returns",
        re.compile(
            r"\b(guaranteed?\s+returns?|double\s+my\s+money|risk-?free\s+returns?)\b",
            re.I,
        ),
    ),
]


def route_query(query: str) -> RouteDecision:
    """
    If ``advisory`` patterns match, block retrieval and use §7.1 educational refusal.

    Factual questions (NAV, expense ratio, exit load, etc.) should not match.
    """
    q = (query or "").strip()
    if not q:
        return RouteDecision(allow_retrieval=False, advisory=True, matched_rule="empty_query")

    for rule_id, pat in _ADVISORY_RULES:
        if pat.search(q):
            return RouteDecision(allow_retrieval=False, advisory=True, matched_rule=rule_id)

    return RouteDecision(allow_retrieval=True, advisory=False, matched_rule=None)
