"""Model-free extractive summarization baselines."""

from __future__ import annotations

import math
import re
from clinical_note_summarization.data.preprocessing import split_sentences

_WORD_RE = re.compile(r"[A-Za-z0-9']+")
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "in", "is", "it", "of", "on", "or", "that", "the", "to", "was", "with",
}


def lead_k(text: str, k: int = 3) -> str:
    """Return the first ``k`` sentences, a transparent extractive baseline."""
    if k <= 0:
        raise ValueError("k must be positive.")
    return " ".join(split_sentences(text)[:k])


def _sentence_words(sentence: str) -> set[str]:
    return {
        word.lower()
        for word in _WORD_RE.findall(sentence)
        if word.lower() not in _STOPWORDS
    }


def textrank(text: str, k: int = 3) -> str:
    """Rank sentences using a small TextRank implementation with no downloads."""
    if k <= 0:
        raise ValueError("k must be positive.")
    sentences = split_sentences(text)
    if len(sentences) <= k:
        return " ".join(sentences)
    words = [_sentence_words(sentence) for sentence in sentences]
    scores = [1.0] * len(sentences)
    for _ in range(20):
        updated = []
        for index, current in enumerate(words):
            score = 0.15
            for other_index, other in enumerate(words):
                if index == other_index or not current or not other:
                    continue
                overlap = len(current & other)
                if overlap:
                    similarity = overlap / math.log1p(len(current)) / math.log1p(len(other))
                    score += 0.85 * similarity * scores[other_index]
            updated.append(score)
        scores = updated
    selected = sorted(range(len(sentences)), key=lambda index: scores[index], reverse=True)[:k]
    return " ".join(sentences[index] for index in sorted(selected))
