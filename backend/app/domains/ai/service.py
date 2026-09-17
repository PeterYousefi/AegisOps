"""AI assessment orchestration.

Ties together the workflow, the provider, the validation pipeline, persistence,
and audit events. All AI output is validated before storage; on failure a safe
fallback is stored and an audit event records the failure.
"""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.domains.ai.models import IncidentAssessment
from app.domains.ai.validation import validate_assessment
from app.domains.ai.workflow import build_context
from app.domains.audit import service as audit_service
from app.domains.incidents import service as incident_service
from app.shared.container import get_ai_provider
from app.shared.enums import AuditEventType, IncidentStatus, ValidationStatus
from app.shared.state_machine import can_transition


def _persist_assessment(
    session: Session, incident_id: str, model, provider_name: str, valid: bool
) -> IncidentAssessment:
    assessment = IncidentAssessment(
        incident_id=incident_id,
        provider=provider_name,
        executive_summary=model.executive_summary,
        severity=model.severity,
        affected_services=list(model.affected_services),
        likely_root_cause=model.likely_root_cause,
        confidence_score=model.confidence_score,
        evidence_references=list(model.evidence_references),
        runbook_references=list(model.runbook_references),
        recommended_next_steps=list(model.recommended_next_steps),
        uncertainties=list(model.uncertainties),
        safety_notes=list(model.safety_notes),
        validation_status=(
            ValidationStatus.VALID if valid else ValidationStatus.INVALID_FALLBACK
        ),
    )
    session.add(assessment)
    session.flush()
    return assessment


def generate_incident_assessment(
    session: Session, incident_id: str
) -> IncidentAssessment:
    """Run the assessment workflow for an incident and persist the result."""
    incident = incident_service.get_incident_or_404(session, incident_id)

    audit_service.record_event(
        session, incident_id, AuditEventType.ASSESSMENT_REQUESTED
    )

    context = build_context(session, incident)
    provider = get_ai_provider()
    raw = provider.generate_assessment(context)
    result = validate_assessment(raw, context)

    assessment = _persist_assessment(
        session,
        incident_id,
        result.model,
        getattr(provider, "name", "unknown"),
        result.is_valid,
    )

    if result.is_valid:
        # Advance a freshly detected incident into investigation.
        if can_transition(incident.status, IncidentStatus.INVESTIGATING):
            previous = incident.status.value
            incident.status = IncidentStatus.INVESTIGATING
            session.flush()
            audit_service.record_event(
                session,
                incident_id,
                AuditEventType.ASSESSMENT_GENERATED,
                previous_state=previous,
                new_state=incident.status.value,
                metadata={"assessment_id": assessment.id},
            )
        else:
            audit_service.record_event(
                session,
                incident_id,
                AuditEventType.ASSESSMENT_GENERATED,
                metadata={"assessment_id": assessment.id},
            )
    else:
        audit_service.record_event(
            session,
            incident_id,
            AuditEventType.ASSESSMENT_VALIDATION_FAILED,
            metadata={"reason": result.reason, "assessment_id": assessment.id},
        )

    session.commit()
    return assessment


def generate_post_incident_report(session: Session, incident_id: str):
    """Generate and persist a post-incident report (only after mitigation)."""
    from app.domains.ai.models import PostIncidentReport
    from app.domains.ai.schemas import PostIncidentReportModel
    from app.shared.enums import IncidentStatus
    from app.shared.errors import ValidationError as DomainValidationError

    incident = incident_service.get_incident_or_404(session, incident_id)
    if incident.status not in (IncidentStatus.MITIGATED, IncidentStatus.RESOLVED):
        raise DomainValidationError(
            "A post-incident report can only be generated after the incident is "
            f"mitigated (current status={incident.status.value})."
        )

    context = build_context(session, incident)
    provider = get_ai_provider()
    raw = provider.generate_report(context)

    # Validate strictly; on failure, refuse rather than store unvalidated output.
    from pydantic import ValidationError as PydanticValidationError

    try:
        model = PostIncidentReportModel.model_validate(raw)
    except PydanticValidationError:
        audit_service.record_event(
            session,
            incident_id,
            AuditEventType.ASSESSMENT_VALIDATION_FAILED,
            metadata={"stage": "report"},
        )
        session.commit()
        raise DomainValidationError("The generated report failed validation.")

    report = PostIncidentReport(
        incident_id=incident_id,
        provider=getattr(provider, "name", "unknown"),
        timeline_summary=model.timeline_summary,
        customer_impact_summary=model.customer_impact_summary,
        root_cause_summary=model.root_cause_summary,
        remediation_summary=model.remediation_summary,
        follow_up_actions=list(model.follow_up_actions),
        lessons_learned=list(model.lessons_learned),
    )
    session.add(report)
    session.flush()

    audit_service.record_event(
        session,
        incident_id,
        AuditEventType.POST_INCIDENT_REPORT_GENERATED,
        metadata={"report_id": report.id},
    )
    session.commit()
    return report


def get_latest_report(session: Session, incident_id: str):
    from app.domains.ai.models import PostIncidentReport

    stmt = (
        select(PostIncidentReport)
        .where(PostIncidentReport.incident_id == incident_id)
        .order_by(desc(PostIncidentReport.created_at))
        .limit(1)
    )
    return session.scalar(stmt)


def get_latest_assessment(
    session: Session, incident_id: str
) -> IncidentAssessment | None:
    """Return the most recent assessment for an incident, if any."""
    stmt = (
        select(IncidentAssessment)
        .where(IncidentAssessment.incident_id == incident_id)
        .order_by(desc(IncidentAssessment.created_at))
        .limit(1)
    )
    return session.scalar(stmt)
