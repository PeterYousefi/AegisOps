"""Explicit AI workflow steps.

These functions gather grounding data and build the IncidentContext passed to
the provider. Only retrieved evidence and retrieved runbooks are included — the
provider never sees the full corpus.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.ai.provider import (
    EvidenceContext,
    IncidentContext,
    RunbookContext,
)
from app.domains.evidence import repository as evidence_repo
from app.domains.incidents.models import Incident
from app.domains.runbooks.models import Runbook
from app.domains.runbooks.retrieval.keyword import KeywordRunbookRetriever


def collect_relevant_evidence(session: Session, incident_id: str) -> list[EvidenceContext]:
    """Gather the incident's evidence as provider context."""
    records = evidence_repo.list_evidence(session, incident_id)
    return [
        EvidenceContext(
            id=r.id,
            evidence_type=(
                r.evidence_type.value
                if hasattr(r.evidence_type, "value")
                else str(r.evidence_type)
            ),
            summary=r.summary,
            payload=r.payload or {},
        )
        for r in records
    ]


def retrieve_relevant_runbooks(
    session: Session, incident: Incident, k: int = 3
) -> list[RunbookContext]:
    """Retrieve the top-k runbooks relevant to the incident."""
    all_runbooks = list(session.scalars(select(Runbook)).all())
    query = f"{incident.title} {incident.affected_service}"
    retriever = KeywordRunbookRetriever()
    results = retriever.retrieve(query, all_runbooks, k=k)
    return [
        RunbookContext(
            id=res.runbook.id,
            slug=res.runbook.slug,
            title=res.runbook.title,
            content_markdown=res.runbook.content_markdown,
        )
        for res in results
    ]


def build_context(session: Session, incident: Incident) -> IncidentContext:
    """Assemble the grounding context for an incident."""
    return IncidentContext(
        incident_id=incident.id,
        title=incident.title,
        affected_service=incident.affected_service,
        evidence=collect_relevant_evidence(session, incident.id),
        runbooks=retrieve_relevant_runbooks(session, incident),
    )
