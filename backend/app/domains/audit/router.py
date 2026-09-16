"""HTTP routes for the append-only audit trail (read-only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.audit import repository as audit_repo
from app.domains.incidents import service as incident_service
from app.domains.incidents.schemas import AuditEventOut
from app.shared.db import get_db

router = APIRouter(prefix="/incidents", tags=["audit"])


@router.get("/{incident_id}/audit", response_model=list[AuditEventOut])
def list_audit_events(
    incident_id: str, db: Session = Depends(get_db)
) -> list[AuditEventOut]:
    incident_service.get_incident_or_404(db, incident_id)
    events = audit_repo.list_events_for_incident(db, incident_id)
    return [AuditEventOut.model_validate(e) for e in events]
