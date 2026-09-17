"""Validation pipeline turning untrusted AI output into trusted data.

Steps:
1. Parse the raw payload into the strict Pydantic model.
2. Verify every cited evidence/runbook ID exists in the provided context.
3. On any failure, return a conservative safe-fallback assessment.

The caller records the appropriate audit event and persists the result.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from app.domains.ai.provider import IncidentContext
from app.domains.ai.schemas import (
    IncidentAssessmentModel,
    RemediationProposalModel,
)


@dataclass
class AssessmentValidation:
    """Result of validating a raw assessment payload."""

    model: IncidentAssessmentModel
    is_valid: bool
    reason: str | None = None


def _safe_fallback(context: IncidentContext, reason: str) -> IncidentAssessmentModel:
    """A conservative assessment used when validation fails.

    Invents nothing: no evidence/runbook references, low confidence, clear
    uncertainty, and a safety note. Never surfaces raw model output.
    """
    return IncidentAssessmentModel(
        executive_summary=(
            "Automated analysis could not be validated. Manual review is required."
        ),
        severity="sev3",
        affected_services=[context.affected_service],
        likely_root_cause="Undetermined — automated assessment failed validation.",
        confidence_score=0.0,
        evidence_references=[],
        runbook_references=[],
        recommended_next_steps=[
            "Review the incident evidence manually.",
        ],
        uncertainties=[
            "The automated assessment did not pass validation and was discarded.",
        ],
        safety_notes=[
            "No remediation should be taken based on the discarded assessment.",
            "All remediation requires human approval and is simulated.",
        ],
    )


def validate_assessment(
    raw: dict, context: IncidentContext
) -> AssessmentValidation:
    """Validate a raw assessment payload against schema + reference existence."""
    valid_evidence_ids = {e.id for e in context.evidence}
    valid_runbook_ids = {r.id for r in context.runbooks}

    # Step 1: strict schema parse.
    try:
        model = IncidentAssessmentModel.model_validate(raw)
    except ValidationError as exc:
        return AssessmentValidation(
            model=_safe_fallback(context, "schema_validation_failed"),
            is_valid=False,
            reason=f"schema_validation_failed: {exc.error_count()} error(s)",
        )

    # Step 2: reference-existence checks.
    unknown_evidence = [
        eid for eid in model.evidence_references if eid not in valid_evidence_ids
    ]
    unknown_runbooks = [
        rid for rid in model.runbook_references if rid not in valid_runbook_ids
    ]
    if unknown_evidence or unknown_runbooks:
        return AssessmentValidation(
            model=_safe_fallback(context, "unknown_reference"),
            is_valid=False,
            reason=(
                "unknown_reference: "
                f"evidence={unknown_evidence} runbooks={unknown_runbooks}"
            ),
        )

    return AssessmentValidation(model=model, is_valid=True)


@dataclass
class ProposalValidation:
    """Result of validating a raw remediation proposal payload."""

    model: RemediationProposalModel | None
    is_valid: bool
    reason: str | None = None


def validate_proposal(raw: dict, context: IncidentContext) -> ProposalValidation:
    """Validate a raw remediation proposal against schema + reference existence.

    Unlike assessments, an invalid proposal has no safe fallback action — we
    refuse to fabricate a remediation. The caller records an audit event and
    surfaces the failure instead of proposing anything.
    """
    valid_evidence_ids = {e.id for e in context.evidence}
    valid_runbook_ids = {r.id for r in context.runbooks}

    try:
        model = RemediationProposalModel.model_validate(raw)
    except ValidationError as exc:
        return ProposalValidation(
            model=None,
            is_valid=False,
            reason=f"schema_validation_failed: {exc.error_count()} error(s)",
        )

    if not model.required_approval:
        return ProposalValidation(
            model=None,
            is_valid=False,
            reason="required_approval must be true",
        )

    unknown_evidence = [
        eid for eid in model.evidence_references if eid not in valid_evidence_ids
    ]
    unknown_runbooks = [
        rid for rid in model.runbook_references if rid not in valid_runbook_ids
    ]
    if unknown_evidence or unknown_runbooks:
        return ProposalValidation(
            model=None,
            is_valid=False,
            reason=(
                "unknown_reference: "
                f"evidence={unknown_evidence} runbooks={unknown_runbooks}"
            ),
        )

    return ProposalValidation(model=model, is_valid=True)
