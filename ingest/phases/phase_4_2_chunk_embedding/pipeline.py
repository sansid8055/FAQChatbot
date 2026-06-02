"""Chunk normalized runs and embed locally (phase 4.2)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ingest.phases.phase_4_2_chunk_embedding import config
from ingest.phases.phase_4_2_chunk_embedding.embed_local import embed_chunks
from ingest.phases.phase_4_2_chunk_embedding.markdown_segments import split_normalized_document
from ingest.phases.phase_4_2_chunk_embedding.pack_chunks import pack_sections_to_chunks
from ingest.phases.phase_4_2_chunk_embedding.types import ChunkRecord
from ingest.phases.phase_4_0_scheduler_scraping.types import utc_now_iso

logger = logging.getLogger(__name__)


def discover_latest_normalized_run(base: Path) -> Path | None:
    if not base.is_dir():
        return None
    candidates: list[Path] = []
    for p in base.iterdir():
        if p.is_dir() and (p / "normalize_manifest.json").is_file():
            candidates.append(p)
    if not candidates:
        return None
    candidates.sort(key=lambda x: x.name, reverse=True)
    return candidates[0]


def run_chunk_embed(
    normalized_run_dir: Path,
    *,
    embed: bool = True,
) -> dict[str, Any]:
    normalized_run_dir = normalized_run_dir.resolve()
    nm_path = normalized_run_dir / "normalize_manifest.json"
    facts_path = normalized_run_dir / "scheme_facts.json"
    if not nm_path.is_file():
        raise FileNotFoundError(f"Missing {nm_path}")
    if not facts_path.is_file():
        raise FileNotFoundError(f"Missing {facts_path}")

    nm = json.loads(nm_path.read_text(encoding="utf-8"))
    facts_doc = json.loads(facts_path.read_text(encoding="utf-8"))
    run_id = nm["run_id"]
    facts_by_scheme = {f["scheme_id"]: f for f in facts_doc.get("facts", [])}

    all_chunks: list[ChunkRecord] = []
    for finfo in nm.get("files", []):
        if finfo.get("status") != "ok":
            continue
        sid = finfo["scheme_id"]
        frow = facts_by_scheme.get(sid)
        if not frow:
            logger.warning("No scheme_facts row for %s — skip", sid)
            continue
        txt_path = normalized_run_dir / f"{sid}.txt"
        if not txt_path.is_file():
            logger.warning("Missing normalized txt %s — skip", txt_path)
            continue
        text = txt_path.read_text(encoding="utf-8")
        sections = split_normalized_document(text)
        chunks = pack_sections_to_chunks(
            sections,
            source_url=frow["source_url"],
            source_type="groww_scheme_page",
            scheme_id=sid,
            scheme_name=frow["scheme_name"],
            amc=frow["amc"],
            fetched_at=frow["fetched_at"],
            normalized_text_hash=frow.get("normalized_text_hash") or "",
        )
        all_chunks.extend(chunks)

    out_dir = (config.chunked_output_dir() / run_id).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    chunks_path = out_dir / "chunks.jsonl"
    with chunks_path.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c.to_jsonable(), ensure_ascii=False) + "\n")

    embed_path = out_dir / "embeddings.jsonl"
    embed_count = 0
    embed_dims = config.EMBEDDING_DIMENSIONS
    if embed:
        logger.info(
            "Embedding %d chunks locally with %s", len(all_chunks), config.EMBEDDING_MODEL_ID
        )
        rows = embed_chunks(all_chunks)
        with embed_path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
                embed_count += 1
        if rows:
            embed_dims = len(rows[0]["embedding"])
    else:
        if embed_path.exists():
            embed_path.unlink()

    manifest = {
        "run_id": run_id,
        "normalized_run_path": str(normalized_run_dir),
        "chunked_at": utc_now_iso(),
        "embedding_model_id": config.EMBEDDING_MODEL_ID,
        "embedding_dimensions": embed_dims,
        "chunk_count": len(all_chunks),
        "chunks_jsonl": f"{run_id}/chunks.jsonl",
        "embeddings_jsonl": f"{run_id}/embeddings.jsonl" if embed else None,
        "embedded_count": embed_count,
        "target_tokens": config.TARGET_TOKENS,
        "max_tokens": config.MAX_TOKENS,
        "overlap_tokens": config.OVERLAP_TOKENS,
    }
    (out_dir / "chunk_run_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    logger.info("Wrote %s (%d chunks, %d embedded)", out_dir, len(all_chunks), embed_count)
    return manifest
