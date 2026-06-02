"""Templated §7.1 refusal + single educational link (AMFI/SEBI class)."""

from __future__ import annotations

from runtime.phase_6_generation.types import GenerationResult
from runtime.phase_7_safety import config


def _uv(body: str, url: str, footer: str) -> str:
    return f"{body.strip()}\n\n{url.strip()}\n\n{footer.strip()}"


def educational_refusal(*, router_rule: str | None) -> GenerationResult:
    url = config.educational_url()
    if router_rule == "pii_heuristic":
        body = (
            "For your privacy, do not share PAN, Aadhaar, account numbers, OTPs, email, or phone in chat. "
            "For general mutual-fund education, see the link below."
        )
    elif router_rule == "empty_query":
        body = "Please ask a specific factual question about a scheme from our indexed sources."
    else:
        body = (
            "I cannot provide investment advice, compare funds, or recommend what you should buy. "
            "For general mutual-fund education in India, see the official resource below."
        )
    footer = "Educational link (not from your indexed scheme pages)."
    return GenerationResult(
        body=body,
        citation_url=url,
        footer=footer,
        user_visible=_uv(body, url, footer),
        model="phase7-router",
        validation_ok=True,
        fallback_used=False,
        raw_model_response=router_rule,
        advisory_refusal=True,
        router_reason=router_rule,
    )
