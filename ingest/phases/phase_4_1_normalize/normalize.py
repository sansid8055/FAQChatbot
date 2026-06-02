"""Run normalization over a raw scrape directory."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from ingest.phases.phase_4_1_normalize import config
from ingest.phases.phase_4_1_normalize.facts import build_scheme_facts
from ingest.phases.phase_4_1_normalize.html_fallback import html_to_fallback_text
from ingest.phases.phase_4_1_normalize.next_data import extract_mf_server_side_data
from ingest.phases.phase_4_1_normalize.text_builder import build_normalized_text
from ingest.phases.phase_4_1_normalize.types import (
    NormalizeFileResult,
    NormalizeRunManifest,
    SchemeFacts,
)

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    from ingest.phases.phase_4_0_scheduler_scraping.types import utc_now_iso as u

    return u()


def discover_latest_raw_run(raw_base: Path) -> Path | None:
    """Pick newest child directory of raw_base that contains manifest.json."""
    if not raw_base.is_dir():
        return None
    candidates: list[Path] = []
    for p in raw_base.iterdir():
        if p.is_dir() and (p / "manifest.json").is_file():
            candidates.append(p)
    if not candidates:
        return None
    candidates.sort(key=lambda x: x.name, reverse=True)
    return candidates[0]


def run_normalize(
    raw_run_dir: Path,
    *,
    output_base: Path | None = None,
) -> NormalizeRunManifest:
    """
    Read data/raw/<run_id>/manifest.json and *.html, write data/normalized/<run_id>/.
    """
    raw_run_dir = raw_run_dir.resolve()
    manifest_path = raw_run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing scrape manifest: {manifest_path}")

    scrape_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_id = scrape_manifest["run_id"]
    amc = (raw_run_dir / "amc.txt").read_text(encoding="utf-8").strip()

    out_base = (output_base or config.normalized_output_dir()).resolve()
    out_dir = out_base / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    normalized_at = _utc_now_iso()
    file_results: list[NormalizeFileResult] = []
    facts_list: list[SchemeFacts] = []

    for row in scrape_manifest.get("results", []):
        if row.get("status") != "ok":
            continue
        scheme_id = row["scheme_id"]
        scheme_name = row["scheme_name"]
        source_url = row["url"]
        fetched_at = row["fetched_at"]
        raw_hash = row["content_hash"]
        html_path = raw_run_dir / f"{scheme_id}.html"

        err: str | None = None
        status = "ok"
        txt_rel: str | None = None
        norm_hash: str | None = None
        text_body: str
        extraction_source: str
        mfd = None

        try:
            html = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            err = str(exc)
            file_results.append(
                NormalizeFileResult(
                    scheme_id=scheme_id,
                    status="read_error",
                    txt_relative_path=None,
                    normalized_text_hash=None,
                    error_message=err,
                )
            )
            continue

        mfd = extract_mf_server_side_data(html)
        if mfd:
            extraction_source = "next_data"
            text_body = build_normalized_text(
                mfd,
                scheme_name=scheme_name,
                source_url=source_url,
                fetched_at=fetched_at,
                amc=amc,
            )
        else:
            extraction_source = "fallback_html"
            logger.warning("Using HTML fallback for %s", scheme_id)
            text_body = html_to_fallback_text(html)
            text_body = (
                f"# {scheme_name}\n\n"
                f"- Source URL: {source_url}\n"
                f"- Fetched at (UTC): {fetched_at}\n\n"
                "## Extracted page text (fallback)\n\n"
                f"{text_body}\n"
            )

        norm_hash = hashlib.sha256(text_body.encode("utf-8")).hexdigest()
        txt_name = f"{scheme_id}.txt"
        txt_path = out_dir / txt_name
        txt_path.write_text(text_body, encoding="utf-8")
        txt_rel = f"{run_id}/{txt_name}"

        if mfd:
            facts_list.append(
                build_scheme_facts(
                    mfd,
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    amc=amc,
                    source_url=source_url,
                    fetched_at=fetched_at,
                    raw_content_hash=raw_hash,
                    extraction_source=extraction_source,
                    normalized_text_hash=norm_hash,
                )
            )
        else:
            facts_list.append(
                SchemeFacts(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    amc=amc,
                    source_url=source_url,
                    fetched_at=fetched_at,
                    raw_content_hash=raw_hash,
                    nav=None,
                    nav_as_of=None,
                    minimum_sip_inr=None,
                    minimum_lumpsum_inr=None,
                    fund_size_aum_cr=None,
                    expense_ratio_percent=None,
                    expense_ratio_raw=None,
                    groww_rating_score=None,
                    riskometer_label=None,
                    benchmark_name=None,
                    exit_load_summary=None,
                    category=None,
                    sub_category=None,
                    plan_type=None,
                    extraction_source=extraction_source,
                    normalized_text_hash=norm_hash,
                )
            )

        file_results.append(
            NormalizeFileResult(
                scheme_id=scheme_id,
                status=status,
                txt_relative_path=txt_rel,
                normalized_text_hash=norm_hash,
                error_message=err,
            )
        )

    facts_path = out_dir / "scheme_facts.json"
    facts_payload = {
        "run_id": run_id,
        "normalized_at": normalized_at,
        "amc": amc,
        "facts": [f.to_jsonable() for f in facts_list],
    }
    facts_path.write_text(json.dumps(facts_payload, indent=2), encoding="utf-8")
    facts_rel = f"{run_id}/scheme_facts.json"

    run_manifest = NormalizeRunManifest(
        run_id=run_id,
        raw_run_path=str(raw_run_dir),
        normalized_at=normalized_at,
        amc=amc,
        files=file_results,
        facts_relative_path=facts_rel,
    )
    (out_dir / "normalize_manifest.json").write_text(
        json.dumps(run_manifest.to_jsonable(), indent=2),
        encoding="utf-8",
    )
    logger.info("Normalized run %s -> %s", run_id, out_dir)
    return run_manifest
