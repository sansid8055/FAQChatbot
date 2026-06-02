"""Chunk records for phase 4.2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ChunkRecord:
    chunk_id: str
    source_url: str
    source_type: str
    scheme_id: str
    scheme_name: str
    amc: str
    fetched_at: str
    normalized_text_hash: str
    section_title: str | None
    chunk_index: int
    chunk_text: str
    chunk_text_hash: str
    embedding_model_id: str

    def to_jsonable(self) -> dict[str, Any]:
        return asdict(self)
