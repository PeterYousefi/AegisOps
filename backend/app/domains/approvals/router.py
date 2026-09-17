"""HTTP routes for approving/rejecting remediation proposals."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.approvals import service
from app.domains.remediation.schemas import ApprovalOut, ApprovalRequest
from app.shared.db import get_db

router = APIRouter(prefix="/proposals", tags=["approvals"])


@router.post("/{proposal_id}/approve", response_model=ApprovalOut)
def approve(
    proposal_id: str,
    body: ApprovalRequest | None = None,
    db: Session = Depends(get_db),
) -> ApprovalOut:
    approval = service.approve_proposal(
        db, proposal_id, comment=body.comment if body else None
    )
    return ApprovalOut.model_validate(approval)


@router.post("/{proposal_id}/reject", response_model=ApprovalOut)
def reject(
    proposal_id: str,
    body: ApprovalRequest | None = None,
    db: Session = Depends(get_db),
) -> ApprovalOut:
    approval = service.reject_proposal(
        db, proposal_id, comment=body.comment if body else None
    )
    return ApprovalOut.model_validate(approval)
