"""Unit tests for the deterministic MockAIProvider."""

from __future__ import annotations

from app.domains.ai.mock_provider import MockAIProvider
from app.domains.ai.provider import EvidenceContext, IncidentContext, RunbookContext
from app.domains.ai.schemas import (
    IncidentAssessmentModel,
    PostIncidentReportModel,
    RemediationProposalModel,
)


def _full_context() -> IncidentContext:
    return IncidentContext(
        incident_id="i1",
        title="Checkout API elevated 5xx errors after deploy",
        affected_service="checkout-api",
        evidence=[
            EvidenceContext("e-alert", "alert", "5xx alert", {}),
            EvidenceContext("e-metric", "metric", "error spike", {}),
            EvidenceContext("e-log", "log", "payment timeout", {}),
            EvidenceContext("e-deploy", "deployment", "release deployed", {}),
        ],
        runbooks=[
            RunbookContext("r-rollback", "rollback-procedure", "Rollback", "..."),
        ],
    )


def _sparse_context() -> IncidentContext:
    # No deployment/log/metric -> insufficient evidence.
    return IncidentContext(
        incident_id="i2",
        title="Something is wrong",
        affected_service="checkout-api",
        evidence=[EvidenceContext("e-note", "operator_note", "seems slow", {})],
        runbooks=[],
    )


def test_assessment_is_schema_valid_and_confident_with_evidence() -> None:
    provider = MockAIProvider()
    ctx = _full_context()
    raw = provider.generate_assessment(ctx)
    model = IncidentAssessmentModel.model_validate(raw)
    assert model.confidence_score >= 0.7
    # Only cites IDs present in the context.
    assert set(model.evidence_references) <= {e.id for e in ctx.evidence}
    assert set(model.runbook_references) <= {r.id for r in ctx.runbooks}


def test_assessment_insufficient_evidence_mode() -> None:
    provider = MockAIProvider()
    raw = provider.generate_assessment(_sparse_context())
    model = IncidentAssessmentModel.model_validate(raw)
    assert model.confidence_score <= 0.5
    assert len(model.uncertainties) > 0


def test_proposal_is_schema_valid_and_requires_approval() -> None:
    provider = MockAIProvider()
    raw = provider.generate_proposal(_full_context())
    model = RemediationProposalModel.model_validate(raw)
    assert model.required_approval is True
    assert model.action_type.value == "rollback_deployment"


def test_report_is_schema_valid() -> None:
    provider = MockAIProvider()
    raw = provider.generate_report(_full_context())
    PostIncidentReportModel.model_validate(raw)


def test_deterministic_output() -> None:
    provider = MockAIProvider()
    ctx = _full_context()
    assert provider.generate_assessment(ctx) == provider.generate_assessment(ctx)
    assert provider.generate_proposal(ctx) == provider.generate_proposal(ctx)
