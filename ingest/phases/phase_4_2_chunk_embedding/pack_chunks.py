"""Token-aware greedy packing with overlap (BAAI/bge-small-en-v1.5 tokenizer)."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import replace

from ingest.phases.phase_4_2_chunk_embedding.config import (
    EMBEDDING_MODEL_ID,
    MAX_INPUT_TOKENS,
    MAX_TOKENS,
    OVERLAP_TOKENS,
    TARGET_TOKENS,
)
from ingest.phases.phase_4_2_chunk_embedding.markdown_segments import Section
from ingest.phases.phase_4_2_chunk_embedding.tokenizer import decode_tail, tok_len
from ingest.phases.phase_4_2_chunk_embedding.types import ChunkRecord

logger = logging.getLogger(__name__)


def _format_section(sec: Section) -> str:
    if sec.section_title:
        return f"## {sec.section_title}\n\n{sec.body}"
    return sec.body


def _split_oversized(body: str, max_tok: int) -> list[str]:
    parts: list[str] = []
    lines = body.splitlines()
    cur: list[str] = []
    for line in lines:
        trial = "\n".join(cur + [line])
        if tok_len(trial) <= max_tok:
            cur.append(line)
        else:
            if cur:
                parts.append("\n".join(cur))
            if tok_len(line) > max_tok:
                step = max(200, max_tok * 3)
                for i in range(0, len(line), step):
                    chunk = line[i : i + step]
                    while tok_len(chunk) > max_tok and len(chunk) > 50:
                        chunk = chunk[: len(chunk) * 8 // 10]
                    parts.append(chunk)
                cur = []
            else:
                cur = [line]
    if cur:
        parts.append("\n".join(cur))
    return parts if parts else [body[: max_tok * 4]]


def _join_parts(parts: list[str]) -> str:
    return "\n\n".join(p for p in parts if p).strip()


def _projected_tokens(overlap: str | None, buf: list[str], next_seg: str | None) -> int:
    p: list[str] = []
    if overlap:
        p.append(overlap)
    p.extend(buf)
    if next_seg is not None:
        p.append(next_seg)
    return tok_len(_join_parts(p)) if p else 0


def pack_sections_to_chunks(
    sections: list[Section],
    *,
    source_url: str,
    source_type: str,
    scheme_id: str,
    scheme_name: str,
    amc: str,
    fetched_at: str,
    normalized_text_hash: str,
) -> list[ChunkRecord]:
    segments: list[str] = []
    seg_meta: list[str | None] = []
    for sec in sections:
        formatted = _format_section(sec)
        if tok_len(formatted) > MAX_TOKENS:
            for piece in _split_oversized(formatted, MAX_TOKENS):
                segments.append(piece)
                seg_meta.append(sec.section_title)
        else:
            segments.append(formatted)
            seg_meta.append(sec.section_title)

    chunks: list[ChunkRecord] = []
    overlap: str | None = None
    buf: list[str] = []
    buf_titles: list[str | None] = []
    chunk_index_counter = 0

    def emit_current() -> None:
        nonlocal overlap, buf, buf_titles, chunk_index_counter
        if not buf and not overlap:
            return
        parts: list[str] = []
        if overlap:
            parts.append(overlap)
        parts.extend(buf)
        text = _join_parts(parts)
        if not text:
            buf = []
            buf_titles = []
            return
        while tok_len(text) > MAX_INPUT_TOKENS:
            text = text[: len(text) * 9 // 10]
            logger.warning("Truncated chunk to respect MAX_INPUT_TOKENS (%d)", MAX_INPUT_TOKENS)
        titles = [t for t in buf_titles if t]
        section_title: str | None
        if not titles:
            section_title = None
        elif len(titles) == 1:
            section_title = titles[0]
        else:
            section_title = titles[0] + " (+more)"

        c_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cid = hashlib.sha256(
            f"{source_url}\n{chunk_index_counter}\n{EMBEDDING_MODEL_ID}".encode("utf-8")
        ).hexdigest()
        chunks.append(
            ChunkRecord(
                chunk_id=cid,
                source_url=source_url,
                source_type=source_type,
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                amc=amc,
                fetched_at=fetched_at,
                normalized_text_hash=normalized_text_hash,
                section_title=section_title,
                chunk_index=chunk_index_counter,
                chunk_text=text,
                chunk_text_hash=c_hash,
                embedding_model_id=EMBEDDING_MODEL_ID,
            )
        )
        chunk_index_counter += 1
        overlap = decode_tail(text, OVERLAP_TOKENS)
        buf = []
        buf_titles = []

    for seg, title in zip(segments, seg_meta, strict=True):
        if buf and _projected_tokens(overlap, buf, seg) > TARGET_TOKENS:
            emit_current()
        buf.append(seg)
        buf_titles.append(title)

    emit_current()

    seen: set[str] = set()
    unique: list[ChunkRecord] = []
    for c in chunks:
        if c.chunk_text_hash in seen:
            continue
        seen.add(c.chunk_text_hash)
        unique.append(c)

    final: list[ChunkRecord] = []
    for i, c in enumerate(unique):
        cid = hashlib.sha256(
            f"{c.source_url}\n{i}\n{EMBEDDING_MODEL_ID}".encode("utf-8")
        ).hexdigest()
        final.append(replace(c, chunk_index=i, chunk_id=cid))
    return final
