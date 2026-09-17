"""Strict Pydantic schemas for AI-generated content.

All AI output is treated as untrusted and must validate against these strict
models (extra fields forbidden, types and ranges enforced) before it is
displayed, stored, or acted upon. Reference-existence checks (evidence/runbook
IDs must exist) are applied separately by the validation pipeline.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import ActionType, RiskLevel, Severity

_STRICT = ConfigDict(extra="forbid")


class IncidentAssessmentModel(BaseModel):
    """Strict schema for an AI incident assessment."""

    model_config = _STRICT

    executive_summary: str = Field(min_length=1)
    severity: Severity
    affected_services: list[str] = Field(default_factory=list)
    likely_root_cause: str = Field(min_length=1)
    confidence_score: float = Field(ge=0.0, le=1.0)
    evidence_references: list[str] = Field(default_factory=list)
    runbook_references: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


class RemediationProposalModel(BaseModel):
    """Strict schema for an AI remediation proposal."""

    model_config = _STRICT

    action_type: ActionType
    action_description: str = Field(min_length=1)
    justification: str = Field(min_length=1)
    risk_level: RiskLevel
    blast_radius: str = Field(min_length=1)
    prerequisites: list[str] = Field(default_factory=list)
    rollback_plan: str = Field(min_length=1)
    expected_outcome: str = Field(min_length=1)
    required_approval: bool = True
    evidence_references: list[str] = Field(default_factory=list)
    runbook_references: list[str] = Field(default_factory=list)


class PostIncidentReportModel(BaseModel):
    """Strict schema for an AI post-incident report."""

    model_config = _STRICT

    timeline_summary: str = Field(min_length=1)
    customer_impact_summary: str = Field(min_length=1)
    root_cause_summary: str = Field(min_length=1)
    remediation_summary: str = Field(min_length=1)
    follow_up_actions: list[str] = Field(default_factory=list)
    lessons_learned: list[str] = Field(default_factory=list)
