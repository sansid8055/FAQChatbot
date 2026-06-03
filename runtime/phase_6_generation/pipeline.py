"""Phase 6: retrieval → Groq generation → validation (rag-architecture.md §6, §7.2)."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from runtime.phase_5_retrieval.types import RetrievalResult
from runtime.phase_6_generation import config
from runtime.phase_6_generation.allowlist import load_allowlisted_urls
from runtime.phase_6_generation.groq_llm import groq_chat_json
from runtime.phase_6_generation.pack_context import build_user_message, footer_date_from_fetched_at
from runtime.phase_6_generation.prompts import STRICT_RETRY_SUFFIX, SYSTEM_PROMPT
from runtime.phase_6_generation.types import GenerationResult
from runtime.phase_6_generation.validate_output import validate_generation

logger = logging.getLogger(__name__)


def _user_visible(body: str, citation_url: str, footer: str) -> str:
    return f"{body.strip()}\n\n{citation_url.strip()}\n\n{footer.strip()}"


def _templated_fallback(
    retrieval: RetrievalResult,
    *,
    allow: frozenset[str],
    footer_date: str,
    reason: str,
) -> GenerationResult:
    url = retrieval.citation_url.strip() if retrieval.citation_url else ""
    if not url and allow:
        url = sorted(allow)[0]
    footer = f"Last updated from sources: {footer_date}"
    body = (
        "I found relevant information in the indexed sources, but couldn't generate a validated concise answer. "
        "Please refer to the official scheme document linked below for complete details."
    )
    return GenerationResult(
        body=body,
        citation_url=url,
        footer=footer,
        user_visible=_user_visible(body, url, footer),
        model="template",
        validation_ok=True,
        fallback_used=True,
        raw_model_response=reason,
        advisory_refusal=False,
        router_reason=None,
    )


def _no_context_result(allow: frozenset[str]) -> GenerationResult:
    url = sorted(allow)[0] if allow else ""
    footer = "Last updated from sources: unknown"
    body = "No matching indexed sources were retrieved for this question."
    return GenerationResult(
        body=body,
        citation_url=url,
        footer=footer,
        user_visible=_user_visible(body, url, footer) if url else f"{body}\n\n{footer}",
        model="none",
        validation_ok=True,
        fallback_used=True,
        raw_model_response=None,
        advisory_refusal=False,
        router_reason=None,
    )


def _parse_generation_dict(parsed: dict) -> tuple[str, str, str]:
    body = str(parsed.get("body", "")).strip()
    cit = str(parsed.get("citation_url", "")).strip()
    foot = str(parsed.get("footer", "")).strip()
    return body, cit, foot


def generate(
    retrieval: RetrievalResult,
    *,
    registry_path: Path | None = None,
) -> GenerationResult:
    reg = registry_path or config.url_registry_path()
    allow = load_allowlisted_urls(reg)
    footer_date = footer_date_from_fetched_at(retrieval.citation_fetched_at)
    required_footer_prefix = f"Last updated from sources: {footer_date}"

    if not retrieval.contexts or not (retrieval.citation_url or "").strip():
        return _no_context_result(allow)

    user_msg = build_user_message(retrieval, footer_date=footer_date)

    def call_llm(*, retry: bool, validation_reason: str = "") -> tuple[str, str, str, str, str]:
        system = SYSTEM_PROMPT + (STRICT_RETRY_SUFFIX if retry else "")
        u = user_msg
        if validation_reason:
            u += f"\n\nValidation error to fix: {validation_reason}"
        parsed, raw, model = groq_chat_json(system=system, user=u)
        b, c, f = _parse_generation_dict(parsed)
        return b, c, f, raw, model

    try:
        body, cit, foot, raw, model = call_llm(retry=False)
    except Exception as e:
        logger.exception("Groq call failed: %s", e)
        return _templated_fallback(
            retrieval, allow=allow, footer_date=footer_date, reason=str(e)
        )

    ok, reason = validate_generation(
        body=body,
        citation_url=cit,
        footer=foot,
        required_citation=retrieval.citation_url,
        required_footer_prefix=required_footer_prefix,
        allowlisted_urls=allow,
    )

    if not ok:
        logger.warning("First generation failed validation: %s", reason)
        time.sleep(2)
        try:
            body2, cit2, foot2, raw2, model = call_llm(retry=True, validation_reason=reason)
            raw = raw + "\n--- retry ---\n" + raw2
            body, cit, foot = body2, cit2, foot2
            ok, reason = validate_generation(
                body=body,
                citation_url=cit,
                footer=foot,
                required_citation=retrieval.citation_url,
                required_footer_prefix=required_footer_prefix,
                allowlisted_urls=allow,
            )
        except Exception as e:
            logger.exception("Groq retry failed: %s", e)
            return _templated_fallback(
                retrieval, allow=allow, footer_date=footer_date, reason=str(e)
            )

    if not ok:
        return _templated_fallback(
            retrieval, allow=allow, footer_date=footer_date, reason=reason
        )

    return GenerationResult(
        body=body,
        citation_url=cit,
        footer=foot,
        user_visible=_user_visible(body, cit, foot),
        model=model,
        validation_ok=True,
        fallback_used=False,
        raw_model_response=raw,
        advisory_refusal=False,
        router_reason=None,
    )
