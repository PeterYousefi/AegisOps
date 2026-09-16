"""Append-only data access for audit events.

This repository intentionally exposes only append and read operations. There
are no update or delete methods — the audit trail is append-only by design.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.audit.models import AuditEvent


def append_event(session: Session, event: AuditEvent) -> AuditEvent:
    """Append a new audit event. (No update/delete is provided by design.)"""
    session.add(event)
    session.flush()
    return event


def list_events_for_incident(session: Session, incident_id: str) -> list[AuditEvent]:
    """Return audit events for an incident, oldest first."""
    stmt = (
        select(AuditEvent)
        .where(AuditEvent.incident_id == incident_id)
        .order_by(AuditEvent.created_at.asc())
    )
    return list(session.scalars(stmt).all())
