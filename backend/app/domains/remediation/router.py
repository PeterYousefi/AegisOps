"""HTTP routes for remediation proposals."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.remediation import service
from app.domains.remediation.schemas import ProposalOut
from app.shared.db import get_db

router = APIRouter(prefix="/incidents", tags=["remediation"])


@router.post("/{incident_id}/proposals", response_model=ProposalOut)
def create_proposal(incident_id: str, db: Session = Depends(get_db)) -> ProposalOut:
    proposal = service.generate_proposal(db, incident_id)
    return ProposalOut.model_validate(proposal)


@router.get("/{incident_id}/proposals", response_model=list[ProposalOut])
def list_proposals(incident_id: str, db: Session = Depends(get_db)) -> list[ProposalOut]:
    return [ProposalOut.model_validate(p) for p in service.list_proposals(db, incident_id)]
