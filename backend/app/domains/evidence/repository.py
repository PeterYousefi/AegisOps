"""Data access for evidence records."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.evidence.models import EvidenceRecord
from app.shared.enums import EvidenceType


def list_evidence(
    session: Session,
    incident_id: str,
    evidence_type: EvidenceType | None = None,
) -> list[EvidenceRecord]:
    """Return evidence for an incident, optionally filtered by type."""
    stmt = select(EvidenceRecord).where(EvidenceRecord.incident_id == incident_id)
    if evidence_type is not None:
        stmt = stmt.where(EvidenceRecord.evidence_type == evidence_type)
    stmt = stmt.order_by(EvidenceRecord.observed_at.asc().nulls_last())
    return list(session.scalars(stmt).all())
