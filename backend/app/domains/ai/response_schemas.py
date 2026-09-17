"""API response schemas for AI artifacts (distinct from the strict input schemas)."""

from __future__ import annotations

import datetime as _dt

from pydantic import BaseModel, ConfigDict


class AssessmentOut(BaseModel):
    """API representation of a stored incident assessment."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    provider: str
    executive_summary: str
    severity: str
    affected_services: list[str]
    likely_root_cause: str
    confidence_score: float
    evidence_references: list[str]
    runbook_references: list[str]
    recommended_next_steps: list[str]
    uncertainties: list[str]
    safety_notes: list[str]
    validation_status: str
    created_at: _dt.datetime
