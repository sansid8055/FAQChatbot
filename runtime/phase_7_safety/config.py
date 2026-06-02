"""Phase 7 — safety / refusal config (rag-architecture.md §7)."""

from __future__ import annotations

import os


def educational_url() -> str:
    """AMFI/SEBI-style general investor education (§7.1); not the Groww corpus allowlist."""
    return os.environ.get(
        "EDUCATIONAL_URL",
        "https://www.amfiindia.in/investor-corner/investor-education",
    ).strip()
