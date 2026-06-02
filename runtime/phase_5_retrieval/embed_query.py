"""Encode user queries with the same BGE model + prefix as ingest (rag-architecture.md query-time)."""

from __future__ import annotations

import threading
from typing import Any

import numpy as np

from runtime.phase_5_retrieval import config

_model: Any = None
_model_init_lock = threading.Lock()
# SentenceTransformer / underlying torch are not safe for concurrent encode from
# multiple request threads; serialize inference while sharing one loaded model.
_encode_lock = threading.Lock()


def _get_model() -> Any:
    global _model
    if _model is None:
        with _model_init_lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer

                _model = SentenceTransformer(config.EMBEDDING_MODEL_ID)
    return _model


def embed_query(text: str) -> list[float]:
    """Return L2-normalized embedding (384-dim for ``bge-small-en-v1.5``)."""
    prefixed = config.BGE_QUERY_PREFIX + text.strip()
    model = _get_model()
    with _encode_lock:
        vec = model.encode(prefixed, normalize_embeddings=True)
    if isinstance(vec, np.ndarray):
        return [float(x) for x in vec.tolist()]
    return [float(x) for x in vec]
