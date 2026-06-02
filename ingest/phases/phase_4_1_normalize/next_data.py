"""Extract Next.js __NEXT_DATA__ payload from Groww HTML."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

_NEXT_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(?P<json>[^<]+)</script>',
    re.DOTALL,
)


def extract_mf_server_side_data(html: str) -> dict[str, Any] | None:
    """Return mfServerSideData dict or None if missing / invalid."""
    m = _NEXT_RE.search(html)
    if not m:
        logger.warning("__NEXT_DATA__ script tag not found")
        return None
    try:
        payload = json.loads(m.group("json"))
    except json.JSONDecodeError as exc:
        logger.warning("Invalid __NEXT_DATA__ JSON: %s", exc)
        return None
    try:
        mfd = payload["props"]["pageProps"]["mfServerSideData"]
    except (KeyError, TypeError):
        logger.warning("mfServerSideData missing in pageProps")
        return None
    if not isinstance(mfd, dict):
        return None
    return mfd
