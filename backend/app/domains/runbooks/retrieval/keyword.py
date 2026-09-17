"""Deterministic keyword-based runbook retrieval.

Scoring is explainable and repeatable: each query term contributes a weighted
amount depending on where it matches (keywords/tags > title > content). Ties
are broken by slug so ordering is stable across runs.
"""

from __future__ import annotations

import re

from app.domains.runbooks.models import Runbook
from app.domains.runbooks.retrieval.base import RetrievalResult

# Match weights by field. Metadata (curated keywords/tags) ranks highest.
WEIGHT_KEYWORD = 3.0
WEIGHT_TAG = 3.0
WEIGHT_TITLE = 2.0
WEIGHT_CONTENT = 1.0

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Very common words that carry no retrieval signal.
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "after", "before", "at", "by", "from",
}


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


class KeywordRunbookRetriever:
    """Rank runbooks by weighted keyword overlap with the query."""

    def retrieve(
        self, query: str, runbooks: list[Runbook], k: int = 3
    ) -> list[RetrievalResult]:
        query_terms = set(_tokenize(query))
        results: list[RetrievalResult] = []

        for runbook in runbooks:
            score = 0.0
            matched: set[str] = set()

            keyword_terms = {t.lower() for t in (runbook.keywords or [])}
            tag_terms = {t.lower() for t in (runbook.tags or [])}
            title_terms = set(_tokenize(runbook.title))
            content_terms = set(_tokenize(runbook.content_markdown))

            for term in query_terms:
                if term in keyword_terms:
                    score += WEIGHT_KEYWORD
                    matched.add(term)
                if term in tag_terms:
                    score += WEIGHT_TAG
                    matched.add(term)
                if term in title_terms:
                    score += WEIGHT_TITLE
                    matched.add(term)
                if term in content_terms:
                    score += WEIGHT_CONTENT
                    matched.add(term)

            if score > 0:
                results.append(
                    RetrievalResult(
                        runbook=runbook,
                        score=round(score, 4),
                        matched_terms=sorted(matched),
                    )
                )

        # Deterministic order: score desc, then slug asc for stable ties.
        results.sort(key=lambda r: (-r.score, r.runbook.slug))
        return results[:k]
