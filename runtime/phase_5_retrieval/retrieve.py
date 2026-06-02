"""Chroma dense retrieval, merge-by-URL, citation pick (rag-architecture.md §5.2–5.3)."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

from runtime.phase_5_retrieval import config
from runtime.phase_5_retrieval.types import MergedContext, RetrievalResult

# Shared Chroma collection may not tolerate concurrent ``.query`` calls; serialize reads.
_chroma_query_lock = threading.Lock()


@dataclass
class _Hit:
    chunk_id: str
    distance: float
    document: str
    metadata: dict[str, Any]


def _flatten_query_results(results: dict[str, Any]) -> list[_Hit]:
    ids = (results.get("ids") or [[]])[0] or []
    dists = (results.get("distances") or [[]])[0] or []
    docs = (results.get("documents") or [[]])[0] or []
    metas = (results.get("metadatas") or [[]])[0] or []
    hits: list[_Hit] = []
    for i, cid in enumerate(ids):
        d = float(dists[i]) if i < len(dists) else 0.0
        doc = docs[i] if i < len(docs) else ""
        meta = metas[i] if i < len(metas) and metas[i] else {}
        hits.append(_Hit(chunk_id=cid, distance=d, document=str(doc or ""), metadata=dict(meta)))
    return hits


def merge_by_source_url(hits: list[_Hit]) -> list[MergedContext]:
    """§5.2.4 — merge chunks that share ``source_url``; keep best (lowest) distance as group score."""
    by_url: dict[str, list[_Hit]] = {}
    order: list[str] = []
    for h in hits:
        url = str(h.metadata.get("source_url") or "")
        if not url:
            url = "__missing_url__"
        if url not in by_url:
            order.append(url)
            by_url[url] = []
        by_url[url].append(h)

    merged: list[MergedContext] = []
    for url in order:
        group = by_url[url]
        best_d = min(x.distance for x in group)
        texts: list[str] = []
        cids: list[str] = []
        meta0 = group[0].metadata
        for x in sorted(group, key=lambda h: h.distance):
            if x.document.strip():
                texts.append(x.document.strip())
            cids.append(x.chunk_id)
        text = "\n\n".join(texts)
        merged.append(
            MergedContext(
                source_url=url if url != "__missing_url__" else "",
                text=text,
                distance=best_d,
                scheme_id=str(meta0.get("scheme_id") or ""),
                scheme_name=str(meta0.get("scheme_name") or ""),
                fetched_at=str(meta0.get("fetched_at") or ""),
                chunk_ids=cids,
            )
        )
    merged.sort(key=lambda m: m.distance)
    return merged


def query_chroma(
    collection: Any,
    query_embedding: list[float],
    *,
    top_k: int | None = None,
    where: dict[str, Any] | None = None,
) -> list[_Hit]:
    k = top_k or config.retrieval_top_k()
    with _chroma_query_lock:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
    return _flatten_query_results(results)


def retrieve_from_chroma(
    collection: Any,
    query: str,
    query_embedding: list[float],
    *,
    scheme_filter: str | None = None,
) -> RetrievalResult:
    where: dict[str, Any] | None = None
    if scheme_filter:
        where = {"scheme_id": scheme_filter}

    hits = query_chroma(collection, query_embedding, where=where)
    contexts = merge_by_source_url(hits)

    if not contexts or not contexts[0].source_url:
        return RetrievalResult(
            query=query,
            scheme_filter=scheme_filter,
            contexts=contexts,
            citation_url="",
            citation_fetched_at="",
            citation_scheme_id="",
        )

    top = contexts[0]
    return RetrievalResult(
        query=query,
        scheme_filter=scheme_filter,
        contexts=contexts,
        citation_url=top.source_url,
        citation_fetched_at=top.fetched_at,
        citation_scheme_id=top.scheme_id,
    )
