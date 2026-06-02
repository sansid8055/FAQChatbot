"""Fallback plain text when __NEXT_DATA__ is unavailable."""

from __future__ import annotations

import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def html_to_fallback_text(html: str, max_chars: int = 400_000) -> str:
    """Strip scripts/styles and emit whitespace-collapsed body text."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [ln.strip() for ln in text.splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[truncated]"
    return text.strip()
