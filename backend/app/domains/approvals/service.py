"""Human approval workflow for remediation proposals."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.approvals.models import RemediationApproval
from app.domains.audit import service as audit_service
from app.domains.audit.service import DEFAULT_ACTOR_ID, DEFAULT_ACTOR_TYPE
from app.domains.incidents import service as incident_service
from app.domains.remediation import service as remediation_service
from app.domains.remediation.models import RemediationProposal
from app.shared.enums import (
    ApprovalDecision,
    AuditEventType,
    IncidentStatus,
    ProposalStatus,
)
from app.shared.errors import ValidationError
from app.shared.state_machine import assert_transition


def _record_approval(
    session: Session,
    proposal: RemediationProposal,
    decision: ApprovalDecision,
    comment: str | None,
) -> RemediationApproval:
    approval = RemediationApproval(
        proposal_id=proposal.id,
        decision=decision,
        actor_type=DEFAULT_ACTOR_TYPE,
        actor_id=DEFAULT_ACTOR_ID,
        comment=comment,
    )
    session.add(approval)
    session.flush()
    return approval


def approve_proposal(
    session: Session, proposal_id: str, comment: str | None = None
) -> RemediationApproval:
    """Approve a pending proposal. Incident remains awaiting_approval until execute."""
    proposal = remediation_service.get_proposal_or_404(session, proposal_id)
    if proposal.status != ProposalStatus.PENDING:
        raise ValidationError(
            f"Only a pending proposal can be approved (status={proposal.status.value})."
        )

    approval = _record_approval(session, proposal, ApprovalDecision.APPROVED, comment)
    proposal.status = ProposalStatus.APPROVED
    session.flush()

    audit_service.record_event(
        session,
        proposal.incident_id,
        AuditEventType.REMEDIATION_APPROVED,
        metadata={"proposal_id": proposal.id, "approval_id": approval.id},
    )
    session.commit()
    return approval


def reject_proposal(
    session: Session, proposal_id: str, comment: str | None = None
) -> RemediationApproval:
    """Reject a pending proposal and return the incident to investigating."""
    proposal = remediation_service.get_proposal_or_404(session, proposal_id)
    if proposal.status != ProposalStatus.PENDING:
        raise ValidationError(
            f"Only a pending proposal can be rejected (status={proposal.status.value})."
        )

    approval = _record_approval(session, proposal, ApprovalDecision.REJECTED, comment)
    proposal.status = ProposalStatus.REJECTED
    session.flush()

    incident = incident_service.get_incident_or_404(session, proposal.incident_id)
    previous = incident.status.value
    if incident.status == IncidentStatus.AWAITING_APPROVAL:
        assert_transition(incident.status, IncidentStatus.INVESTIGATING)
        incident.status = IncidentStatus.INVESTIGATING
        session.flush()

    audit_service.record_event(
        session,
        proposal.incident_id,
        AuditEventType.REMEDIATION_REJECTED,
        previous_state=previous,
        new_state=incident.status.value,
        metadata={"proposal_id": proposal.id, "approval_id": approval.id},
    )
    session.commit()
    return approval


def latest_approval(
    session: Session, proposal_id: str
) -> RemediationApproval | None:
    stmt = (
        select(RemediationApproval)
        .where(RemediationApproval.proposal_id == proposal_id)
        .order_by(RemediationApproval.created_at.desc())
        .limit(1)
    )
    return session.scalar(stmt)


def has_approval(session: Session, proposal_id: str) -> bool:
    """True if the proposal has an APPROVED decision (used as the execute guard)."""
    stmt = select(RemediationApproval).where(
        RemediationApproval.proposal_id == proposal_id,
        RemediationApproval.decision == ApprovalDecision.APPROVED,
    )
    return session.scalar(stmt) is not None
