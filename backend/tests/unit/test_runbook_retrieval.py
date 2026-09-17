"""Unit tests for deterministic keyword runbook retrieval."""

from __future__ import annotations

from app.domains.runbooks.models import Runbook
from app.domains.runbooks.retrieval.keyword import KeywordRunbookRetriever


def _runbook(slug: str, title: str, keywords: list[str], tags: list[str], content: str) -> Runbook:
    return Runbook(
        slug=slug,
        title=title,
        content_markdown=content,
        keywords=keywords,
        tags=tags,
    )


CORPUS = [
    _runbook(
        "checkout-api-high-error-rate",
        "Checkout API High Error Rate",
        ["checkout", "5xx", "error", "rate"],
        ["checkout", "errors"],
        "Elevated 5xx errors on the checkout api after a deploy.",
    ),
    _runbook(
        "payment-provider-timeout",
        "Payment Provider Timeout",
        ["payment", "timeout", "dependency"],
        ["payment"],
        "Payment provider timeouts cause checkout failures.",
    ),
    _runbook(
        "rollback-procedure",
        "Rollback Procedure",
        ["rollback", "deployment", "revert"],
        ["rollback"],
        "Roll back a bad deployment to the last known good release.",
    ),
]


def test_retrieval_is_deterministic() -> None:
    retriever = KeywordRunbookRetriever()
    query = "checkout 5xx error rate after deploy"
    r1 = retriever.retrieve(query, CORPUS, k=3)
    r2 = retriever.retrieve(query, CORPUS, k=3)
    assert [r.runbook.slug for r in r1] == [r.runbook.slug for r in r2]
    assert [r.score for r in r1] == [r.score for r in r2]


def test_top_result_is_most_relevant() -> None:
    retriever = KeywordRunbookRetriever()
    results = retriever.retrieve("checkout 5xx error rate", CORPUS, k=3)
    assert results[0].runbook.slug == "checkout-api-high-error-rate"
    assert results[0].score > 0
    assert "checkout" in results[0].matched_terms


def test_scores_are_explainable_and_ordered() -> None:
    retriever = KeywordRunbookRetriever()
    results = retriever.retrieve("payment timeout", CORPUS, k=3)
    # payment-provider-timeout should rank first for this query.
    assert results[0].runbook.slug == "payment-provider-timeout"
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_no_match_returns_empty() -> None:
    retriever = KeywordRunbookRetriever()
    results = retriever.retrieve("kubernetes networking", CORPUS, k=3)
    assert results == []


def test_k_limits_results() -> None:
    retriever = KeywordRunbookRetriever()
    results = retriever.retrieve("checkout payment rollback deployment error", CORPUS, k=2)
    assert len(results) <= 2
