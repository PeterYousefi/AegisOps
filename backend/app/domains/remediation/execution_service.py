"""Simulated remediation execution with a mandatory prior-approval guard."""

from __future__ import annotations

import datetime as _dt

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.domains.approvals import service as approvals_service
from app.domains.audit import service as audit_service
from app.domains.incidents import service as incident_service
from app.domains.remediation import service as remediation_service
from app.domains.remediation.executor import SimulatedRemediationExecutor
from app.domains.remediation.models import RemediationExecution
from app.shared.enums import (
    AuditEventType,
    ExecutionStatus,
    IncidentStatus,
    ProposalStatus,
)
from app.shared.errors import ValidationError
from app.shared.state_machine import assert_transition


def _utcnow() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def execute_proposal(
    session: Session, proposal_id: str, *, fail: bool = False
) -> RemediationExecution:
    """Run the simulated remediation for an approved proposal.

    Guard: refuses to execute unless the proposal has a prior APPROVED decision.
    Success -> incident mitigated. Failure -> incident returns to investigating,
    with the proposal and the failed execution preserved.
    """
    proposal = remediation_service.get_proposal_or_404(session, proposal_id)

    # Mandatory human-approval guard. No approval -> no execution row.
    if not approvals_service.has_approval(session, proposal_id):
        raise ValidationError(
            "Remediation cannot be executed without a prior approval."
        )
    if proposal.status not in (ProposalStatus.APPROVED, ProposalStatus.FAILED):
        raise ValidationError(
            f"Proposal is not in an executable state (status={proposal.status.value})."
        )

    incident = incident_service.get_incident_or_404(session, proposal.incident_id)

    # awaiting_approval -> mitigating
    previous = incident.status.value
    assert_transition(incident.status, IncidentStatus.MITIGATING)
    incident.status = IncidentStatus.MITIGATING
    proposal.status = ProposalStatus.EXECUTING
    session.flush()

    execution = RemediationExecution(
        proposal_id=proposal.id,
        action_type=proposal.action_type,
        status=ExecutionStatus.STARTED,
        started_at=_utcnow(),
    )
    session.add(execution)
    session.flush()

    audit_service.record_event(
        session,
        proposal.incident_id,
        AuditEventType.SIMULATED_REMEDIATION_STARTED,
        previous_state=previous,
        new_state=incident.status.value,
        metadata={"proposal_id": proposal.id, "execution_id": execution.id},
    )

    outcome = SimulatedRemediationExecutor().execute(proposal.action_type, fail=fail)
    execution.completed_at = _utcnow()
    execution.result = outcome.result

    if outcome.succeeded:
        execution.status = ExecutionStatus.SUCCEEDED
        proposal.status = ProposalStatus.EXECUTED
        prev = incident.status.value
        assert_transition(incident.status, IncidentStatus.MITIGATED)
        incident.status = IncidentStatus.MITIGATED
        session.flush()
        audit_service.record_event(
            session,
            proposal.incident_id,
            AuditEventType.SIMULATED_REMEDIATION_COMPLETED,
            previous_state=prev,
            new_state=incident.status.value,
            metadata={"proposal_id": proposal.id, "execution_id": execution.id},
        )
    else:
        execution.status = ExecutionStatus.FAILED
        execution.failure_reason = outcome.failure_reason
        proposal.status = ProposalStatus.FAILED
        prev = incident.status.value
        # mitigating -> investigating (proposal + failed execution preserved)
        assert_transition(incident.status, IncidentStatus.INVESTIGATING)
        incident.status = IncidentStatus.INVESTIGATING
        session.flush()
        audit_service.record_event(
            session,
            proposal.incident_id,
            AuditEventType.SIMULATED_REMEDIATION_FAILED,
            previous_state=prev,
            new_state=incident.status.value,
            metadata={
                "proposal_id": proposal.id,
                "execution_id": execution.id,
                "failure_reason": outcome.failure_reason,
            },
        )

    session.commit()
    return execution


def get_latest_execution(
    session: Session, proposal_id: str
) -> RemediationExecution | None:
    stmt = (
        select(RemediationExecution)
        .where(RemediationExecution.proposal_id == proposal_id)
        .order_by(desc(RemediationExecution.started_at))
        .limit(1)
    )
    return session.scalar(stmt)
