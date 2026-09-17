"""Runbook retrieval interface and result types.

The retriever abstracts *how* runbooks are found for an incident. The MVP uses
a deterministic keyword implementation; a vector-based implementation can be
added later behind the same interface without changing callers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.domains.runbooks.models import Runbook


@dataclass(frozen=True)
class RetrievalResult:
    """A single ranked runbook with an explainable score."""

    runbook: Runbook
    score: float
    matched_terms: list[str] = field(default_factory=list)


class RunbookRetriever(Protocol):
    """Interface for retrieving relevant runbooks for a query."""

    def retrieve(
        self, query: str, runbooks: list[Runbook], k: int = 3
    ) -> list[RetrievalResult]:
        """Return up to ``k`` runbooks ranked by relevance to ``query``."""
        ...
