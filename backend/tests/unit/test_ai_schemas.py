"""Unit tests for the strict AI Pydantic schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domains.ai.schemas import (
    IncidentAssessmentModel,
    PostIncidentReportModel,
    RemediationProposalModel,
)


def _valid_assessment() -> dict:
    return {
        "executive_summary": "summary",
        "severity": "sev1",
        "affected_services": ["checkout-api"],
        "likely_root_cause": "deploy",
        "confidence_score": 0.8,
        "evidence_references": ["e1"],
        "runbook_references": ["r1"],
        "recommended_next_steps": ["rollback"],
        "uncertainties": [],
        "safety_notes": ["human approval required"],
    }


def test_valid_assessment_parses() -> None:
    model = IncidentAssessmentModel.model_validate(_valid_assessment())
    assert model.confidence_score == 0.8


def test_confidence_out_of_range_rejected() -> None:
    data = _valid_assessment()
    data["confidence_score"] = 1.5
    with pytest.raises(ValidationError):
        IncidentAssessmentModel.model_validate(data)


def test_extra_fields_rejected() -> None:
    data = _valid_assessment()
    data["injected"] = "malicious"
    with pytest.raises(ValidationError):
        IncidentAssessmentModel.model_validate(data)


def test_bad_severity_rejected() -> None:
    data = _valid_assessment()
    data["severity"] = "sev9"
    with pytest.raises(ValidationError):
        IncidentAssessmentModel.model_validate(data)


def test_proposal_requires_valid_action_type() -> None:
    proposal = {
        "action_type": "rollback_deployment",
        "action_description": "roll back",
        "justification": "correlates with deploy",
        "risk_level": "medium",
        "blast_radius": "service only",
        "prerequisites": [],
        "rollback_plan": "roll forward",
        "expected_outcome": "baseline restored",
        "required_approval": True,
        "evidence_references": [],
        "runbook_references": [],
    }
    assert RemediationProposalModel.model_validate(proposal).required_approval is True

    proposal["action_type"] = "delete_database"
    with pytest.raises(ValidationError):
        RemediationProposalModel.model_validate(proposal)


def test_report_requires_all_fields() -> None:
    with pytest.raises(ValidationError):
        PostIncidentReportModel.model_validate({"timeline_summary": "x"})
