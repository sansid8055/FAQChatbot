"""Dataclasses for scrape results and run manifest (phase 4.0)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RegistryEntry:
    url: str
    scheme_id: str
    scheme_name: str
    source_type: str


@dataclass
class ScrapeResult:
    url: str
    scheme_id: str
    scheme_name: str
    source_type: str
    status: str  # ok | http_error | timeout | robots_disallowed | empty_body | fetch_error
    http_status: int | None
    fetched_at: str  # ISO 8601 UTC
    content_hash: str | None  # sha256 of raw bytes, hex
    relative_path: str | None  # path under run dir
    error_message: str | None


@dataclass
class RunManifest:
    run_id: str
    started_at: str
    finished_at: str
    registry_path: str
    results: list[ScrapeResult] = field(default_factory=list)

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "registry_path": self.registry_path,
            "results": [asdict(r) for r in self.results],
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
