"""Build normalized plain-text documents for chunking (chunking-embedding-architecture §3.1)."""

from __future__ import annotations

from typing import Any


def _line(label: str, value: Any) -> str | None:
    if value is None or value == "":
        return None
    return f"- {label}: {value}"


def build_normalized_text(
    mfd: dict[str, Any],
    *,
    scheme_name: str,
    source_url: str,
    fetched_at: str,
    amc: str,
) -> str:
    """Deterministic text from mfServerSideData for RAG chunking."""
    lines: list[str] = [
        f"# {scheme_name}",
        "",
        f"- Source URL: {source_url}",
        f"- Fetched at (UTC): {fetched_at}",
        f"- AMC: {amc}",
        "",
        "## Key metrics",
    ]
    optional = [
        _line("NAV (INR)", mfd.get("nav")),
        _line("NAV as of", mfd.get("nav_date")),
        _line("Minimum SIP (INR)", mfd.get("min_sip_investment")),
        _line("Minimum lumpsum (INR)", mfd.get("min_investment_amount")),
        _line("Fund size / AUM (₹ Cr)", mfd.get("aum")),
        _line("Expense ratio (% p.a.)", mfd.get("expense_ratio")),
        _line("Groww rating (score)", mfd.get("groww_rating")),
        _line("Risk label (NFO risk)", mfd.get("nfo_risk")),
        _line("CRISIL rating", mfd.get("crisil_rating")),
    ]
    lines.extend(s for s in optional if s)
    lines.extend(
        [
            "",
            "## Scheme profile",
            "",
        ]
    )
    profile = [
        _line("Category", mfd.get("category")),
        _line("Sub-category", mfd.get("sub_category")),
        _line("Plan type", mfd.get("plan_type")),
        _line("Benchmark", mfd.get("benchmark_name")),
        _line("Exit load", mfd.get("exit_load")),
        _line("Lock-in", _format_lock_in(mfd.get("lock_in"))),
        _line("Fund manager", mfd.get("fund_manager")),
        _line("Launch date", mfd.get("launch_date")),
        _line("ISIN", mfd.get("isin")),
    ]
    lines.extend(s for s in profile if s)

    desc = mfd.get("description")
    if desc:
        lines.extend(["", "## Investment objective / description", "", str(desc).strip()])

    return "\n".join(lines).strip() + "\n"


def _format_lock_in(lock_in: Any) -> str | None:
    if not isinstance(lock_in, dict):
        return None
    y = lock_in.get("years") or 0
    mo = lock_in.get("months") or 0
    d = lock_in.get("days") or 0
    if not any([y, mo, d]):
        return None
    parts = []
    if y:
        parts.append(f"{y} year(s)")
    if mo:
        parts.append(f"{mo} month(s)")
    if d:
        parts.append(f"{d} day(s)")
    return ", ".join(parts)
