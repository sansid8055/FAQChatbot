"""Package retrieval hits for the LLM (rag-architecture.md §6.1 context packaging)."""

from __future__ import annotations

from runtime.phase_5_retrieval.types import MergedContext, RetrievalResult


def format_context_blocks(retrieval: RetrievalResult) -> str:
    """Each block: Source URL + scheme metadata + chunk text."""
    parts: list[str] = []
    for i, ctx in enumerate(retrieval.contexts):
        header = (
            f"### CONTEXT {i + 1}\n"
            f"Source URL: {ctx.source_url}\n"
            f"scheme_id: {ctx.scheme_id}\n"
            f"scheme_name: {ctx.scheme_name}\n"
            f"fetched_at: {ctx.fetched_at}\n\n"
            f"{ctx.text.strip()}"
        )
        parts.append(header)
    return "\n\n---\n\n".join(parts)


def build_user_message(retrieval: RetrievalResult, *, footer_date: str) -> str:
    blocks = format_context_blocks(retrieval)
    return (
        f"USER_QUESTION:\n{retrieval.query}\n\n"
        f"REQUIRED_CITATION_URL (you must use this exact string for citation_url):\n{retrieval.citation_url}\n\n"
        f"REQUIRED_FOOTER (copy exactly for footer):\nLast updated from sources: {footer_date}\n\n"
        f"{blocks}"
    )


def footer_date_from_fetched_at(iso_ts: str) -> str:
    """Policy §6.2: date from cited source only (phase 5 already selected citation)."""
    if not iso_ts or not iso_ts.strip():
        return "unknown"
    s = iso_ts.strip()
    if "T" in s:
        return s.split("T", 1)[0]
    return s[:10] if len(s) >= 10 else s
