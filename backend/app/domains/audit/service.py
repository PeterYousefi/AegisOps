"""Audit service: append-only recording of meaningful events."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.logging import correlation_id_var
from app.domains.audit import repository as audit_repo
from app.domains.audit.models import AuditEvent
from app.shared.enums import ActorType, AuditEventType

# Default mock operator identity for the local MVP.
DEFAULT_ACTOR_TYPE = ActorType.OPERATOR
DEFAULT_ACTOR_ID = "operator@aegisops.local"


def record_event(
    session: Session,
    incident_id: str | None,
    event_type: AuditEventType,
    *,
    actor_type: ActorType = DEFAULT_ACTOR_TYPE,
    actor_id: str = DEFAULT_ACTOR_ID,
    previous_state: str | None = None,
    new_state: str | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
    """Append an audit event. The trail is append-only (no update/delete)."""
    event = AuditEvent(
        incident_id=incident_id,
        event_type=event_type,
        actor_type=actor_type,
        actor_id=actor_id,
        previous_state=previous_state,
        new_state=new_state,
        event_metadata=metadata or {},
        correlation_id=correlation_id_var.get(),
    )
    return audit_repo.append_event(session, event)
