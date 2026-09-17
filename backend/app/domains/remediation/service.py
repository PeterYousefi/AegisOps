"""Remediation proposal generation and lookup.

A proposal is created from the incident's latest assessment context, validated
strictly, persisted as `pending`, and moves the incident to `awaiting_approval`.
An invalid AI proposal is refused (no fabricated remediation).
"""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.domains.ai import service as ai_service
from app.domains.ai.validation import validate_proposal
from app.domains.ai.workflow import build_context
from app.domains.audit import service as audit_service
from app.domains.incidents import service as incident_service
from app.domains.remediation.models import RemediationProposal
from app.shared.container import get_ai_provider
from app.shared.enums import (
    AuditEventType,
    IncidentStatus,
    ProposalStatus,
)
from app.shared.errors import ValidationError
from app.shared.state_machine import assert_transition


def generate_proposal(session: Session, incident_id: str) -> RemediationProposal:
    """Generate and persist a remediation proposal for an incident."""
    incident = incident_service.get_incident_or_404(session, incident_id)
    context = build_context(session, incident)
    provider = get_ai_provider()

    raw = provider.generate_proposal(context)
    result = validate_proposal(raw, context)

    if not result.is_valid or result.model is None:
        audit_service.record_event(
            session,
            incident_id,
            AuditEventType.ASSESSMENT_VALIDATION_FAILED,
            metadata={"stage": "proposal", "reason": result.reason},
        )
        session.commit()
        raise ValidationError(
            "The generated remediation proposal failed validation and was refused."
        )

    latest_assessment = ai_service.get_latest_assessment(session, incident_id)
    model = result.model

    proposal = RemediationProposal(
        incident_id=incident_id,
        assessment_id=latest_assessment.id if latest_assessment else None,
        action_type=model.action_type,
        action_description=model.action_description,
        justification=model.justification,
        risk_level=model.risk_level,
        blast_radius=model.blast_radius,
        prerequisites=list(model.prerequisites),
        rollback_plan=model.rollback_plan,
        expected_outcome=model.expected_outcome,
        required_approval=True,
        evidence_references=list(model.evidence_references),
        runbook_references=list(model.runbook_references),
        status=ProposalStatus.PENDING,
    )
    session.add(proposal)
    session.flush()

    # investigating -> awaiting_approval
    previous = incident.status.value
    assert_transition(incident.status, IncidentStatus.AWAITING_APPROVAL)
    incident.status = IncidentStatus.AWAITING_APPROVAL
    session.flush()

    audit_service.record_event(
        session,
        incident_id,
        AuditEventType.REMEDIATION_PROPOSED,
        previous_state=previous,
        new_state=incident.status.value,
        metadata={"proposal_id": proposal.id, "action_type": proposal.action_type.value},
    )
    audit_service.record_event(
        session,
        incident_id,
        AuditEventType.APPROVAL_REQUESTED,
        metadata={"proposal_id": proposal.id},
    )

    session.commit()
    return proposal


def list_proposals(session: Session, incident_id: str) -> list[RemediationProposal]:
    stmt = (
        select(RemediationProposal)
        .where(RemediationProposal.incident_id == incident_id)
        .order_by(desc(RemediationProposal.created_at))
    )
    return list(session.scalars(stmt).all())


def get_proposal_or_404(session: Session, proposal_id: str) -> RemediationProposal:
    proposal = session.get(RemediationProposal, proposal_id)
    if proposal is None:
        from app.shared.errors import NotFoundError

        raise NotFoundError(f"Proposal {proposal_id} not found")
    return proposal
