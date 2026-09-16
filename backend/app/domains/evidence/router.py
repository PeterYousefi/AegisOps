"""HTTP routes for incident evidence."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.evidence import repository as evidence_repo
from app.domains.incidents import service as incident_service
from app.domains.incidents.schemas import EvidenceOut
from app.shared.db import get_db
from app.shared.enums import EvidenceType

router = APIRouter(prefix="/incidents", tags=["evidence"])


@router.get("/{incident_id}/evidence", response_model=list[EvidenceOut])
def list_evidence(
    incident_id: str,
    type: EvidenceType | None = None,
    db: Session = Depends(get_db),
) -> list[EvidenceOut]:
    # 404 if the incident does not exist.
    incident_service.get_incident_or_404(db, incident_id)
    records = evidence_repo.list_evidence(db, incident_id, evidence_type=type)
    return [EvidenceOut.model_validate(r) for r in records]
