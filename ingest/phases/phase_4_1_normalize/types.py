"""Dataclasses for normalized output and structured scheme facts (rag-architecture §3.4)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SchemeFacts:
    scheme_id: str
    scheme_name: str
    amc: str
    source_url: str
    fetched_at: str
    raw_content_hash: str
    nav: float | None
    nav_as_of: str | None
    minimum_sip_inr: int | None
    minimum_lumpsum_inr: int | None
    fund_size_aum_cr: float | None
    expense_ratio_percent: float | None
    expense_ratio_raw: str | None
    groww_rating_score: int | None
    riskometer_label: str | None
    benchmark_name: str | None
    exit_load_summary: str | None
    category: str | None
    sub_category: str | None
    plan_type: str | None
    extraction_source: str  # next_data | fallback_html
    normalized_text_hash: str | None  # sha256 of UTF-8 normalized .txt body

    def to_jsonable(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizeFileResult:
    scheme_id: str
    status: str  # ok | no_next_data | read_error
    txt_relative_path: str | None
    normalized_text_hash: str | None
    error_message: str | None


@dataclass
class NormalizeRunManifest:
    run_id: str
    raw_run_path: str
    normalized_at: str
    amc: str
    files: list[NormalizeFileResult] = field(default_factory=list)
    facts_relative_path: str | None = None

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "raw_run_path": self.raw_run_path,
            "normalized_at": self.normalized_at,
            "amc": self.amc,
            "facts_relative_path": self.facts_relative_path,
            "files": [asdict(f) for f in self.files],
        }
