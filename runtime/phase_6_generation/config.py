"""Groq + generation defaults (rag-architecture.md §6)."""

from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    p = os.environ.get("INGEST_REPO_ROOT")
    if p:
        return Path(p).expanduser().resolve()
    return _DEFAULT_ROOT


def url_registry_path() -> Path:
    p = os.environ.get("INGEST_REGISTRY_PATH")
    if p:
        return Path(p).expanduser().resolve()
    return repo_root() / "ingest" / "url_registry" / "urls.yaml"


def groq_api_key() -> str:
    return os.environ.get("GROQ_API_KEY", "").strip()


def groq_model() -> str:
    return os.environ.get(
        "GROQ_MODEL",
        "llama-3.1-8b-instant",
    ).strip()


def groq_temperature() -> float:
    return float(os.environ.get("GROQ_TEMPERATURE", "0.2"))
