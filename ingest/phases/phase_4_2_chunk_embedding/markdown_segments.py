"""Split normalized .txt (markdown-style) into sections for packing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Section:
    """One logical block: optional ## title and body text."""

    section_title: str | None
    body: str


def split_normalized_document(text: str) -> list[Section]:
    """
    Split on markdown headings. Lines with ## (or deeper) start a new section.
    The first `# ` line stays in the opening section (preamble).
    """
    lines = text.splitlines()
    sections: list[Section] = []
    current_title: str | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf
        body = "\n".join(buf).strip()
        if body:
            sections.append(Section(current_title, body))
        buf = []

    for line in lines:
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            continue
        buf.append(line)
    flush()
    return sections
