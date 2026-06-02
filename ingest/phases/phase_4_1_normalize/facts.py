"""Map Groww mfServerSideData to structured scheme facts (rag-architecture §3.4)."""

from __future__ import annotations

from typing import Any

from ingest.phases.phase_4_1_normalize.types import SchemeFacts


def _parse_expense_ratio(val: Any) -> tuple[float | None, str | None]:
    if val is None:
        return None, None
    raw = str(val).strip()
    if not raw:
        return None, None
    try:
        return float(raw), raw
    except ValueError:
        return None, raw


def _int_or_none(val: Any) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _float_or_none(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def build_scheme_facts(
    mfd: dict[str, Any],
    *,
    scheme_id: str,
    scheme_name: str,
    amc: str,
    source_url: str,
    fetched_at: str,
    raw_content_hash: str,
    extraction_source: str,
    normalized_text_hash: str | None,
) -> SchemeFacts:
    exp_pct, exp_raw = _parse_expense_ratio(mfd.get("expense_ratio"))
    risk = mfd.get("nfo_risk")
    risk_str = str(risk).strip() if risk is not None else None

    return SchemeFacts(
        scheme_id=scheme_id,
        scheme_name=scheme_name,
        amc=amc,
        source_url=source_url,
        fetched_at=fetched_at,
        raw_content_hash=raw_content_hash,
        nav=_float_or_none(mfd.get("nav")),
        nav_as_of=(str(mfd["nav_date"]).strip() if mfd.get("nav_date") else None),
        minimum_sip_inr=_int_or_none(mfd.get("min_sip_investment")),
        minimum_lumpsum_inr=_int_or_none(mfd.get("min_investment_amount")),
        fund_size_aum_cr=_float_or_none(mfd.get("aum")),
        expense_ratio_percent=exp_pct,
        expense_ratio_raw=exp_raw,
        groww_rating_score=_int_or_none(mfd.get("groww_rating")),
        riskometer_label=risk_str,
        benchmark_name=(str(mfd["benchmark_name"]).strip() if mfd.get("benchmark_name") else None),
        exit_load_summary=(str(mfd["exit_load"]).strip() if mfd.get("exit_load") else None),
        category=(str(mfd["category"]).strip() if mfd.get("category") else None),
        sub_category=(str(mfd["sub_category"]).strip() if mfd.get("sub_category") else None),
        plan_type=(str(mfd["plan_type"]).strip() if mfd.get("plan_type") else None),
        extraction_source=extraction_source,
        normalized_text_hash=normalized_text_hash,
    )
