"""AI provider interface and the grounding context passed to it.

Providers receive only the retrieved evidence and runbooks for an incident —
never the full corpus — and return raw content that MUST be validated by the
pipeline before use. The MockAIProvider is the default; AzureAIProvider is a
configurable skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class EvidenceContext:
    """Minimal evidence view given to the provider."""

    id: str
    evidence_type: str
    summary: str
    payload: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RunbookContext:
    """Minimal runbook view given to the provider."""

    id: str
    slug: str
    title: str
    content_markdown: str


@dataclass(frozen=True)
class IncidentContext:
    """Everything the provider is allowed to reason over for one incident."""

    incident_id: str
    title: str
    affected_service: str
    evidence: list[EvidenceContext] = field(default_factory=list)
    runbooks: list[RunbookContext] = field(default_factory=list)


class AIProvider(Protocol):
    """Interface for AI providers. Return raw dicts to be validated downstream."""

    def generate_assessment(self, context: IncidentContext) -> dict:
        """Return a raw assessment payload (untrusted, unvalidated)."""
        ...

    def generate_proposal(self, context: IncidentContext) -> dict:
        """Return a raw remediation proposal payload (untrusted, unvalidated)."""
        ...

    def generate_report(self, context: IncidentContext) -> dict:
        """Return a raw post-incident report payload (untrusted, unvalidated)."""
        ...
