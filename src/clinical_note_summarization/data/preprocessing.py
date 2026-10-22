"""Conservative preprocessing for discharge-style clinical notes."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NoteSection:
    title: str
    text: str


@dataclass(frozen=True)
class TextChunk:
    chunk_id: int
    text: str
    token_start: int
    token_end: int


_HEADER_RE = re.compile(
    r"^\s*(?P<title>[A-Z][A-Z0-9 /&()'-]{2,60})\s*:?\s*$"
)
_INLINE_HEADER_RE = re.compile(
    r"^\s*(?P<title>[A-Z][A-Z0-9 /&()'-]{2,60})\s*:\s*(?P<body>.+?)\s*$"
)
_PLACEHOLDER_RE = re.compile(r"_{2,}")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def normalize_placeholders(text: str) -> str:
    """Replace blank-line underscores without deleting surrounding words."""
    return _PLACEHOLDER_RE.sub(" [REDACTED] ", text)


def normalize_note(text: str) -> str:
    """Normalize whitespace while retaining negation, punctuation, and headings."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Note text must be a non-empty string.")
    normalized = normalize_placeholders(text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(line.split()) for line in normalized.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def split_sections(text: str) -> list[NoteSection]:
    """Split discharge-style notes on standalone uppercase section headers."""
    normalized = normalize_note(text)
    sections: list[NoteSection] = []
    current_title = "UNSPECIFIED"
    current_lines: list[str] = []

    def flush() -> None:
        body = " ".join(current_lines).strip()
        if body:
            sections.append(NoteSection(current_title, body))

    for line in normalized.splitlines():
        match = _HEADER_RE.match(line)
        if match:
            flush()
            current_title = match.group("title").strip().rstrip(":")
            current_lines = []
            continue
        inline_match = _INLINE_HEADER_RE.match(line)
        if inline_match:
            flush()
            current_title = inline_match.group("title").strip().rstrip(":")
            current_lines = [inline_match.group("body")]
        else:
            current_lines.append(line)
    flush()
    return sections


def tokenize(text: str) -> list[str]:
    """Use a transparent whitespace tokenizer for reproducible pilot runs."""
    return text.split()


def chunk_text(text: str, max_tokens: int = 256, overlap: int = 32) -> list[TextChunk]:
    """Create overlapping token chunks without requiring a model tokenizer."""
    if max_tokens <= 0 or overlap < 0 or overlap >= max_tokens:
        raise ValueError("Require max_tokens > overlap >= 0.")
    tokens = tokenize(normalize_note(text))
    chunks: list[TextChunk] = []
    step = max_tokens - overlap
    for chunk_id, start in enumerate(range(0, len(tokens), step)):
        end = min(start + max_tokens, len(tokens))
        chunks.append(TextChunk(chunk_id, " ".join(tokens[start:end]), start, end))
        if end == len(tokens):
            break
    return chunks


def split_sentences(text: str) -> list[str]:
    """Split simple clinical prose while preserving sentence punctuation."""
    return [sentence.strip() for sentence in _SENTENCE_RE.split(normalize_note(text)) if sentence.strip()]
