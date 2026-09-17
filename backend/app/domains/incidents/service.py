"""Business logic for incidents."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domains.audit import repository as audit_repo
from app.domains.audit import service as audit_service
from app.domains.evidence import repository as evidence_repo
from app.domains.evidence.models import EvidenceRecord
from app.domains.incidents import repository as incident_repo
from app.domains.incidents.models import Incident
from app.shared.enums import (
    AuditEventType,
    EvidenceType,
    IncidentStatus,
    Severity,
)
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


def _next_reference(session: Session) -> str:
    """Generate the next incident reference code, e.g. 'INC-1004'.

    Uses a base offset so codes look established, plus the current incident
    count. Uniqueness is enforced by the DB column; collisions are astronomically
    unlikely for a demo but the unique constraint is the backstop.
    """
    from sqlalchemy import func, select

    count = session.scalar(select(func.count()).select_from(Incident)) or 0
    return f"INC-{1000 + count + 1}"


def create_incident(
    session: Session,
    *,
    title: str,
    severity: Severity,
    affected_service: str,
    assigned_operator: str | None = None,
) -> Incident:
    """Create a new incident in the `detected` state and record an audit event."""
    incident = Incident(
        reference=_next_reference(session),
        title=title,
        severity=severity,
        status=IncidentStatus.DETECTED,
        affected_service=affected_service,
        assigned_operator=assigned_operator,
    )
    session.add(incident)
    session.flush()

    audit_service.record_event(
        session,
        incident.id,
        AuditEventType.INCIDENT_CREATED,
        new_state=incident.status.value,
        metadata={"title": title, "severity": severity.value},
    )
    session.commit()
    return incident


def add_evidence(
    session: Session,
    incident_id: str,
    *,
    evidence_type: EvidenceType,
    summary: str,
    source: str | None = None,
    payload: dict | None = None,
) -> EvidenceRecord:
    """Attach an evidence record to an incident and record an audit event."""
    # 404 if the incident does not exist.
    get_incident_or_404(session, incident_id)

    evidence = EvidenceRecord(
        incident_id=incident_id,
        evidence_type=evidence_type,
        source=source,
        summary=summary,
        payload=payload or {},
    )
    session.add(evidence)
    session.flush()

    audit_service.record_event(
        session,
        incident_id,
        AuditEventType.EVIDENCE_ADDED,
        metadata={"evidence_id": evidence.id, "evidence_type": evidence_type.value},
    )
    session.commit()
    return evidence


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


def resolve_incident(session: Session, incident_id: str) -> Incident:
    """Mark a mitigated incident as resolved (mitigated -> resolved), audited."""
    incident = get_incident_or_404(session, incident_id)
    previous = incident.status.value
    assert_transition(incident.status, IncidentStatus.RESOLVED)
    incident.status = IncidentStatus.RESOLVED
    session.flush()
    audit_service.record_event(
        session,
        incident_id,
        AuditEventType.INCIDENT_RESOLVED,
        previous_state=previous,
        new_state=incident.status.value,
    )
    session.commit()
    return incident
