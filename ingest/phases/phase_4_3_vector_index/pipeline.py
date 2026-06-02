"""Upsert phase 4.2 JSONL into local on-disk Chroma (phase 4.3)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from chromadb.api.models.Collection import Collection

from ingest.phases.phase_4_0_scheduler_scraping.types import utc_now_iso
from ingest.phases.phase_4_3_vector_index import config
from ingest.phases.phase_4_3_vector_index.chroma_client_factory import create_chroma_client
from ingest.phases.phase_4_3_vector_index.registry_urls import load_allowlist

logger = logging.getLogger(__name__)


def discover_latest_chunked_run(base: Path) -> Path | None:
    """Latest directory under ``base`` with manifest + non-empty embeddings."""
    if not base.is_dir():
        return None
    candidates: list[Path] = []
    for p in base.iterdir():
        if not p.is_dir():
            continue
        man = p / "chunk_run_manifest.json"
        emb = p / "embeddings.jsonl"
        if not man.is_file() or not emb.is_file():
            continue
        try:
            m = json.loads(man.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if int(m.get("embedded_count") or 0) < 1:
            continue
        if emb.stat().st_size == 0:
            continue
        candidates.append(p)
    if not candidates:
        return None
    candidates.sort(key=lambda x: x.name, reverse=True)
    return candidates[0]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _chunk_metadata_for_chroma(
    chunk: dict[str, Any],
    *,
    run_id: str,
    embedding_model_id: str,
) -> dict[str, str | int]:
    """Flatten chunk JSON to Chroma metadata (str / int / float / bool only)."""
    section = chunk.get("section_title")
    return {
        "chunk_id": str(chunk["chunk_id"]),
        "source_url": str(chunk["source_url"]),
        "scheme_id": str(chunk["scheme_id"]),
        "scheme_name": str(chunk.get("scheme_name") or ""),
        "amc": str(chunk.get("amc") or ""),
        "source_type": str(chunk.get("source_type") or ""),
        "fetched_at": str(chunk.get("fetched_at") or ""),
        "chunk_index": int(chunk.get("chunk_index") or 0),
        "section_title": str(section) if section is not None else "",
        "normalized_text_hash": str(chunk.get("normalized_text_hash") or ""),
        "chunk_text_hash": str(chunk.get("chunk_text_hash") or ""),
        "run_id": run_id,
        "embedding_model_id": embedding_model_id,
    }


def _purge_disallowed_schemes(
    collection: Collection,
    allowed_scheme_ids: set[str],
) -> int:
    """Remove points whose ``scheme_id`` is not in the URL registry."""
    data = collection.get(include=["metadatas"])
    ids = data.get("ids") or []
    metas = data.get("metadatas") or []
    to_delete: list[str] = []
    for cid, meta in zip(ids, metas):
        if not meta:
            to_delete.append(cid)
            continue
        sid = meta.get("scheme_id")
        if not isinstance(sid, str) or sid not in allowed_scheme_ids:
            to_delete.append(cid)
    if to_delete:
        collection.delete(ids=to_delete)
        logger.info("Purged %d Chroma records not in url registry", len(to_delete))
    return len(to_delete)


def run_chroma_index(
    chunked_run_dir: Path,
    *,
    chroma_persist: Path | None = None,
    collection_name: str | None = None,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    """
    Join ``chunks.jsonl`` + ``embeddings.jsonl``, upsert into Chroma, purge stale schemes.

    Uses ``chromadb.PersistentClient`` under ``INGEST_CHROMA_DIR`` (default ``data/chroma``).

    Returns manifest dict (written under the chunked run and mirrored under the persist dir).
    """
    chunked_run_dir = chunked_run_dir.resolve()
    man_path = chunked_run_dir / "chunk_run_manifest.json"
    chunks_path = chunked_run_dir / "chunks.jsonl"
    emb_path = chunked_run_dir / "embeddings.jsonl"
    if not man_path.is_file():
        raise FileNotFoundError(f"Missing {man_path}")
    if not chunks_path.is_file():
        raise FileNotFoundError(f"Missing {chunks_path}")
    if not emb_path.is_file():
        raise FileNotFoundError(
            f"Missing {emb_path} — run phase 4.2 without --no-embed before indexing"
        )

    manifest = json.loads(man_path.read_text(encoding="utf-8"))
    run_id = str(manifest["run_id"])
    embedding_model_id = str(manifest.get("embedding_model_id") or "")
    expected_dim = int(manifest.get("embedding_dimensions") or config.EMBEDDING_DIMENSIONS)

    chunks = _read_jsonl(chunks_path)
    embeddings_rows = _read_jsonl(emb_path)
    by_id: dict[str, dict[str, Any]] = {c["chunk_id"]: c for c in chunks}
    emb_by_id: dict[str, list[float]] = {}
    for row in embeddings_rows:
        cid = row["chunk_id"]
        vec = row["embedding"]
        if not isinstance(vec, list):
            raise TypeError(f"embedding for {cid} is not a list")
        if len(vec) != expected_dim:
            raise ValueError(
                f"Chunk {cid}: embedding dim {len(vec)} != expected {expected_dim}"
            )
        emb_by_id[cid] = [float(x) for x in vec]

    missing_emb = [cid for cid in by_id if cid not in emb_by_id]
    if missing_emb:
        raise ValueError(
            f"{len(missing_emb)} chunks lack embeddings (e.g. {missing_emb[:3]!r})"
        )
    orphan_emb = [cid for cid in emb_by_id if cid not in by_id]
    if orphan_emb:
        raise ValueError(f"Embeddings without chunk rows: {orphan_emb[:5]!r}")

    reg = registry_path or config.url_registry_path()
    allowed_schemes, _allowed_urls = load_allowlist(reg)

    skipped_scheme: list[str] = []
    for cid, ch in list(by_id.items()):
        sid = str(ch.get("scheme_id") or "")
        if sid not in allowed_schemes:
            skipped_scheme.append(cid)
            del by_id[cid]
    if skipped_scheme:
        logger.warning(
            "Skipping %d chunks whose scheme_id is not in %s",
            len(skipped_scheme),
            reg,
        )
    if not by_id:
        raise ValueError("No chunks left to index after registry filter")

    client, persist_path = create_chroma_client(chroma_persist=chroma_persist)
    name = collection_name or config.chroma_collection_name()

    collection = client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )

    purged = _purge_disallowed_schemes(collection, allowed_schemes)

    ids: list[str] = []
    embs: list[list[float]] = []
    docs: list[str] = []
    metas: list[dict[str, str | int]] = []
    for cid, ch in by_id.items():
        ids.append(cid)
        embs.append(emb_by_id[cid])
        docs.append(str(ch["chunk_text"]))
        metas.append(
            _chunk_metadata_for_chroma(
                ch, run_id=run_id, embedding_model_id=embedding_model_id
            )
        )

    batch = max(1, config.CHROMA_UPSERT_BATCH)
    for i in range(0, len(ids), batch):
        collection.upsert(
            ids=ids[i : i + batch],
            embeddings=embs[i : i + batch],
            documents=docs[i : i + batch],
            metadatas=metas[i : i + batch],
        )

    current_id_set = set(ids)
    post_get = collection.get(include=[])
    post_ids = list(post_get.get("ids") or [])
    stale_ids = [i for i in post_ids if i not in current_id_set]
    deleted_stale = 0
    del_batch = max(1, config.CHROMA_UPSERT_BATCH)
    for i in range(0, len(stale_ids), del_batch):
        chunk_del = stale_ids[i : i + del_batch]
        collection.delete(ids=chunk_del)
        deleted_stale += len(chunk_del)
    if deleted_stale:
        logger.info(
            "Chroma: deleted %d stale chunk id(s) not present in current run",
            deleted_stale,
        )

    logger.info(
        "Chroma: upserted %d vectors into collection %r at %s",
        len(ids),
        name,
        persist_path,
    )

    index_manifest: dict[str, Any] = {
        "indexed_at": utc_now_iso(),
        "chroma_target": "local_persistent",
        "chunked_run_id": run_id,
        "chunked_run_path": str(chunked_run_dir),
        "collection_name": name,
        "embedding_model_id": embedding_model_id,
        "embedding_dimensions": expected_dim,
        "upserted_chunk_count": len(ids),
        "purged_not_in_registry_count": purged,
        "deleted_stale_chunk_ids_count": deleted_stale,
        "url_registry_path": str(reg.resolve()),
        "chroma_persist_path": str(persist_path),
    }

    manifest_json = json.dumps(index_manifest, indent=2)
    (chunked_run_dir / "chroma_index_manifest.json").write_text(
        manifest_json,
        encoding="utf-8",
    )
    (persist_path / "index_manifest.json").write_text(manifest_json, encoding="utf-8")

    return index_manifest
