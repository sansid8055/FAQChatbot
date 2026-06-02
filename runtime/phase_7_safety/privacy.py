"""Lightweight PII / sensitive-pattern helpers (rag-architecture.md §7.3)."""

from __future__ import annotations

import re

# Indian PAN: 5 letters, 4 digits, 1 letter
_PAN_RE = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.I)

# 12 consecutive digits (Aadhaar-like — heuristic only)
_AADHAAR_LIKE_RE = re.compile(r"\b\d{4}\s*\d{4}\s*\d{4}\b|\b\d{12}\b")

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)

# Indian mobile: 10 digits, often with +91
_PHONE_RE = re.compile(r"(?:\+91[\s-]?)?[6-9]\d{9}\b")


def contains_likely_pan(text: str) -> bool:
    return bool(_PAN_RE.search(text or ""))


def contains_likely_aadhaar(text: str) -> bool:
    return bool(_AADHAAR_LIKE_RE.search(text or ""))


def contains_email(text: str) -> bool:
    return bool(_EMAIL_RE.search(text or ""))


def contains_phone(text: str) -> bool:
    return bool(_PHONE_RE.search(text or ""))


def user_message_looks_sensitive(text: str) -> bool:
    """True if query may include PII — use to refuse or strip before logging."""
    return (
        contains_likely_pan(text)
        or contains_likely_aadhaar(text)
        or contains_email(text)
        or contains_phone(text)
    )


def redact_for_logs(text: str, *, placeholder: str = "[REDACTED]") -> str:
    """Best-effort redaction for log lines (§7.3)."""
    t = text or ""
    t = _PAN_RE.sub(placeholder, t)
    t = _AADHAAR_LIKE_RE.sub(placeholder, t)
    t = _EMAIL_RE.sub(placeholder, t)
    t = _PHONE_RE.sub(placeholder, t)
    return t
