"""Business logic for incidents."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domains.audit import repository as audit_repo
from app.domains.evidence import repository as evidence_repo
from app.domains.incidents import repository as incident_repo
from app.domains.incidents.models import Incident
from app.shared.enums import IncidentStatus, Severity
from app.shared.errors import NotFoundError
from app.shared.state_machine import assert_transition


def list_incidents(
    session: Session,
    status: IncidentStatus | None = None,
    severity: Severity | None = None,
) -> list[Incident]:
    return incident_repo.list_incidents(session, status=status, severity=severity)


def get_incident_or_404(session: Session, incident_id: str) -> Incident:
    incident = incident_repo.get_incident(session, incident_id)
    if incident is None:
        raise NotFoundError(f"Incident {incident_id} not found")
    return incident


def get_incident_detail(session: Session, incident_id: str) -> dict:
    """Return an incident plus its related evidence and audit events."""
    incident = get_incident_or_404(session, incident_id)
    evidence = evidence_repo.list_evidence(session, incident_id)
    audit_events = audit_repo.list_events_for_incident(session, incident_id)
    return {
        "incident": incident,
        "evidence": evidence,
        "audit_events": audit_events,
    }


def change_status(
    session: Session, incident: Incident, target: IncidentStatus
) -> Incident:
    """Change an incident's status, enforcing the state machine.

    Raises InvalidStateTransition (handled as HTTP 409) for disallowed moves.
    """
    assert_transition(incident.status, target)
    incident.status = target
    session.flush()
    return incident
