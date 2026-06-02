"""Scraping service: fetch allowlisted URLs, persist raw HTML, emit manifest.

Implements docs/rag-architecture.md §4.0 (scraping) and §4.2 (per-URL failure).
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
import yaml

from ingest.phases.phase_4_0_scheduler_scraping import config
from ingest.phases.phase_4_0_scheduler_scraping.types import (
    RegistryEntry,
    RunManifest,
    ScrapeResult,
    utc_now_iso,
)

logger = logging.getLogger(__name__)

_SESSION = requests.Session()


def load_registry(path: Path) -> tuple[str, list[RegistryEntry]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "entries" not in data:
        raise ValueError("Registry must be a YAML mapping with 'entries' list")
    amc = str(data.get("amc", ""))
    entries: list[RegistryEntry] = []
    for row in data["entries"]:
        entries.append(
            RegistryEntry(
                url=str(row["url"]).strip(),
                scheme_id=str(row["scheme_id"]).strip(),
                scheme_name=str(row["scheme_name"]).strip(),
                source_type=str(row.get("source_type", "groww_scheme_page")).strip(),
            )
        )
    return amc, entries


def _robots_allowed(url: str, user_agent: str, timeout: float) -> bool:
    """Use requests (same TLS stack as page fetches) to load robots.txt."""
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{origin}/robots.txt"
    rp = RobotFileParser()
    try:
        resp = _SESSION.get(
            robots_url,
            headers={"User-Agent": user_agent},
            timeout=min(timeout, 15.0),
        )
        if resp.status_code != 200 or not resp.text.strip():
            logger.info("No usable robots.txt at %s (status=%s)", robots_url, resp.status_code)
            return True
        rp.set_url(robots_url)
        rp.parse(resp.text.splitlines())
    except Exception as exc:  # noqa: BLE001 — best-effort robots
        logger.warning("Could not read robots.txt for %s: %s — allowing fetch", origin, exc)
        return True
    try:
        return rp.can_fetch(user_agent, url)
    except Exception as exc:  # noqa: BLE001
        logger.warning("robots can_fetch failed for %s: %s — allowing fetch", url, exc)
        return True


def _fetch_url(url: str, user_agent: str, timeout: float) -> tuple[int | None, bytes | None, str | None]:
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
    }
    try:
        resp = _SESSION.get(url, headers=headers, timeout=timeout)
    except requests.Timeout:
        return None, None, "timeout"
    except requests.RequestException as exc:
        return None, None, f"fetch_error: {exc}"
    body = resp.content or b""
    if resp.status_code != 200:
        return resp.status_code, body if body else None, f"http_{resp.status_code}"
    if not body.strip():
        return resp.status_code, None, "empty_body"
    return resp.status_code, body, None


def run_scrape(
    *,
    registry_file: Path | None = None,
    output_base: Path | None = None,
    run_id: str | None = None,
) -> RunManifest:
    reg_path = registry_file or config.registry_path()
    out_base = output_base or config.raw_output_dir()
    ua = config.user_agent()
    delay = config.rate_limit_seconds()
    timeout = config.timeout_seconds()

    started = utc_now_iso()
    rid = run_id or started.replace(":", "").replace("-", "")[:15]

    amc, entries = load_registry(reg_path)
    run_dir = out_base / rid
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "amc.txt").write_text(amc, encoding="utf-8")

    results: list[ScrapeResult] = []
    last_fetch_monotonic: float | None = None

    for entry in entries:
        # Rate limit: spacing between requests
        if last_fetch_monotonic is not None:
            elapsed = time.monotonic() - last_fetch_monotonic
            if elapsed < delay:
                time.sleep(delay - elapsed)

        fetched_at = utc_now_iso()
        rel_path: str | None = None
        content_hash: str | None = None
        http_status: int | None = None
        status = "ok"
        err: str | None = None

        if not _robots_allowed(entry.url, ua, timeout):
            status = "robots_disallowed"
            err = "URL disallowed by robots.txt"
            logger.warning("Skipping %s: %s", entry.url, err)
        else:
            http_status, body, fetch_err = _fetch_url(entry.url, ua, timeout)
            last_fetch_monotonic = time.monotonic()

            if fetch_err == "timeout":
                status = "timeout"
                err = "Request timed out"
            elif fetch_err == "empty_body":
                status = "empty_body"
                err = "Empty response body"
            elif fetch_err and fetch_err.startswith("http_"):
                status = "http_error"
                err = fetch_err
            elif fetch_err:
                status = "fetch_error"
                err = fetch_err
            elif body:
                content_hash = hashlib.sha256(body).hexdigest()
                safe_name = f"{entry.scheme_id}.html"
                target = run_dir / safe_name
                target.write_bytes(body)
                rel_path = f"{rid}/{safe_name}"
            else:
                status = "fetch_error"
                err = "Unknown fetch failure"

        results.append(
            ScrapeResult(
                url=entry.url,
                scheme_id=entry.scheme_id,
                scheme_name=entry.scheme_name,
                source_type=entry.source_type,
                status=status,
                http_status=http_status,
                fetched_at=fetched_at,
                content_hash=content_hash,
                relative_path=rel_path,
                error_message=err,
            )
        )

        if status == "ok":
            logger.info("Scraped OK %s -> %s", entry.url, rel_path)
        else:
            logger.error("Scrape failed %s status=%s err=%s", entry.url, status, err)

    finished = utc_now_iso()
    manifest = RunManifest(
        run_id=rid,
        started_at=started,
        finished_at=finished,
        registry_path=str(reg_path.resolve()),
        results=results,
    )
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.to_jsonable(), indent=2),
        encoding="utf-8",
    )
    logger.info("Wrote manifest %s", manifest_path)
    return manifest
