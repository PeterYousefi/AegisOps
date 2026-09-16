"""HTTP routes for incidents."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.incidents import service
from app.domains.incidents.schemas import (
    AuditEventOut,
    EvidenceOut,
    IncidentDetail,
    IncidentSummary,
)
from app.shared.db import get_db
from app.shared.enums import IncidentStatus, Severity

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentSummary])
def list_incidents(
    status: IncidentStatus | None = None,
    severity: Severity | None = None,
    db: Session = Depends(get_db),
) -> list[IncidentSummary]:
    incidents = service.list_incidents(db, status=status, severity=severity)
    return [IncidentSummary.model_validate(i) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: str, db: Session = Depends(get_db)) -> IncidentDetail:
    detail = service.get_incident_detail(db, incident_id)
    summary = IncidentSummary.model_validate(detail["incident"])
    return IncidentDetail(
        **summary.model_dump(),
        evidence=[EvidenceOut.model_validate(e) for e in detail["evidence"]],
        audit_events=[
            AuditEventOut.model_validate(a) for a in detail["audit_events"]
        ],
    )
