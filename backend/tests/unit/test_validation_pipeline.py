"""Unit tests for the AI assessment validation pipeline."""

from __future__ import annotations

from app.domains.ai.provider import EvidenceContext, IncidentContext, RunbookContext
from app.domains.ai.validation import validate_assessment


def _context() -> IncidentContext:
    return IncidentContext(
        incident_id="i1",
        title="Checkout errors",
        affected_service="checkout-api",
        evidence=[EvidenceContext("e1", "alert", "5xx", {})],
        runbooks=[RunbookContext("r1", "rollback", "Rollback", "...")],
    )


def _valid_raw() -> dict:
    return {
        "executive_summary": "s",
        "severity": "sev1",
        "affected_services": ["checkout-api"],
        "likely_root_cause": "deploy",
        "confidence_score": 0.8,
        "evidence_references": ["e1"],
        "runbook_references": ["r1"],
        "recommended_next_steps": ["rollback"],
        "uncertainties": [],
        "safety_notes": ["approval required"],
    }


def test_valid_output_passes() -> None:
    result = validate_assessment(_valid_raw(), _context())
    assert result.is_valid is True
    assert result.model.confidence_score == 0.8


def test_unknown_evidence_reference_falls_back() -> None:
    raw = _valid_raw()
    raw["evidence_references"] = ["e1", "does-not-exist"]
    result = validate_assessment(raw, _context())
    assert result.is_valid is False
    assert "unknown_reference" in (result.reason or "")
    # Fallback invents nothing.
    assert result.model.evidence_references == []
    assert result.model.confidence_score == 0.0


def test_unknown_runbook_reference_falls_back() -> None:
    raw = _valid_raw()
    raw["runbook_references"] = ["r-nope"]
    result = validate_assessment(raw, _context())
    assert result.is_valid is False


def test_schema_violation_falls_back() -> None:
    raw = _valid_raw()
    raw["confidence_score"] = 2.0  # out of range
    result = validate_assessment(raw, _context())
    assert result.is_valid is False
    assert "schema_validation_failed" in (result.reason or "")
