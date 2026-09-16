"""Data access for incidents."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.incidents.models import Incident
from app.shared.enums import IncidentStatus, Severity


def list_incidents(
    session: Session,
    status: IncidentStatus | None = None,
    severity: Severity | None = None,
) -> list[Incident]:
    """Return incidents, optionally filtered by status and/or severity."""
    stmt = select(Incident)
    if status is not None:
        stmt = stmt.where(Incident.status == status)
    if severity is not None:
        stmt = stmt.where(Incident.severity == severity)
    stmt = stmt.order_by(Incident.created_at.desc())
    return list(session.scalars(stmt).all())


def get_incident(session: Session, incident_id: str) -> Incident | None:
    """Return a single incident by id, or None."""
    return session.get(Incident, incident_id)
