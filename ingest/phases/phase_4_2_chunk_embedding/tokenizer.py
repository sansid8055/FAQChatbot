"""Lazy-loaded BERT WordPiece tokenizer for bge-small-en-v1.5 token counting."""

from __future__ import annotations

import logging

from transformers import AutoTokenizer

from ingest.phases.phase_4_2_chunk_embedding.config import EMBEDDING_MODEL_ID

logger = logging.getLogger(__name__)

_TOKENIZER: AutoTokenizer | None = None


def _get_tokenizer() -> AutoTokenizer:
    global _TOKENIZER  # noqa: PLW0603
    if _TOKENIZER is None:
        logger.info("Loading tokenizer for %s", EMBEDDING_MODEL_ID)
        _TOKENIZER = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_ID)
    return _TOKENIZER


def tok_len(text: str) -> int:
    return len(_get_tokenizer().encode(text, add_special_tokens=False))


def decode_tail(text: str, n_tokens: int) -> str:
    """Return the last n_tokens of text, decoded back to a string."""
    tok = _get_tokenizer()
    ids = tok.encode(text, add_special_tokens=False)
    if len(ids) <= n_tokens:
        return text
    return tok.decode(ids[-n_tokens:])
