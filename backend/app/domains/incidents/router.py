"""HTTP routes for incidents."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.incidents import service
from app.domains.incidents.schemas import (
    AuditEventOut,
    EvidenceCreate,
    EvidenceOut,
    IncidentCreate,
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


@router.post("", response_model=IncidentSummary, status_code=201)
def create_incident(
    body: IncidentCreate, db: Session = Depends(get_db)
) -> IncidentSummary:
    incident = service.create_incident(
        db,
        title=body.title,
        severity=body.severity,
        affected_service=body.affected_service,
        assigned_operator=body.assigned_operator,
    )
    return IncidentSummary.model_validate(incident)


@router.post("/{incident_id}/evidence", response_model=EvidenceOut, status_code=201)
def add_evidence(
    incident_id: str, body: EvidenceCreate, db: Session = Depends(get_db)
) -> EvidenceOut:
    evidence = service.add_evidence(
        db,
        incident_id,
        evidence_type=body.evidence_type,
        summary=body.summary,
        source=body.source,
        payload=body.payload,
    )
    return EvidenceOut.model_validate(evidence)


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
