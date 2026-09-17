"""HTTP routes for remediation proposals."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.remediation import execution_service, service
from app.domains.remediation.schemas import ExecutionOut, ProposalOut
from app.shared.db import get_db
from app.shared.errors import NotFoundError

incidents_router = APIRouter(prefix="/incidents", tags=["remediation"])
proposals_router = APIRouter(prefix="/proposals", tags=["remediation"])


@incidents_router.post("/{incident_id}/proposals", response_model=ProposalOut)
def create_proposal(incident_id: str, db: Session = Depends(get_db)) -> ProposalOut:
    proposal = service.generate_proposal(db, incident_id)
    return ProposalOut.model_validate(proposal)


@incidents_router.get("/{incident_id}/proposals", response_model=list[ProposalOut])
def list_proposals(incident_id: str, db: Session = Depends(get_db)) -> list[ProposalOut]:
    return [ProposalOut.model_validate(p) for p in service.list_proposals(db, incident_id)]


@proposals_router.post("/{proposal_id}/execute", response_model=ExecutionOut)
def execute_proposal(
    proposal_id: str,
    fail: bool = False,
    db: Session = Depends(get_db),
) -> ExecutionOut:
    """Run the simulated remediation. `fail=true` forces the failure path."""
    execution = execution_service.execute_proposal(db, proposal_id, fail=fail)
    return ExecutionOut.model_validate(execution)


@proposals_router.get("/{proposal_id}/execution", response_model=ExecutionOut)
def get_execution(proposal_id: str, db: Session = Depends(get_db)) -> ExecutionOut:
    execution = execution_service.get_latest_execution(db, proposal_id)
    if execution is None:
        raise NotFoundError(f"No execution for proposal {proposal_id}")
    return ExecutionOut.model_validate(execution)
