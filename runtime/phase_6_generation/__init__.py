"""Phase 6 — Generation with Groq (rag-architecture.md §6)."""

from runtime.phase_6_generation.types import GenerationResult

__all__ = ["generate", "GenerationResult"]


def __getattr__(name: str):
    if name == "generate":
        from runtime.phase_6_generation.pipeline import generate

        return generate
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
