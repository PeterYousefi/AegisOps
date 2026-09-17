"""Pydantic response schemas for incidents and their related resources."""

from __future__ import annotations

import datetime as _dt

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import EvidenceType, IncidentStatus, Severity


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    evidence_type: EvidenceType
    source: str | None
    summary: str
    payload: dict
    observed_at: _dt.datetime | None
    created_at: _dt.datetime


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str | None
    event_type: str
    actor_type: str
    actor_id: str
    previous_state: str | None
    new_state: str | None
    # ORM attribute is `event_metadata`; expose it as `metadata` in the API.
    metadata: dict = Field(validation_alias="event_metadata", serialization_alias="metadata")
    correlation_id: str | None
    created_at: _dt.datetime


class IncidentSummary(BaseModel):
    """List-view representation of an incident."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    severity: Severity
    status: IncidentStatus
    affected_service: str
    assigned_operator: str | None
    ai_summary: str | None
    created_at: _dt.datetime
    updated_at: _dt.datetime


class IncidentDetail(IncidentSummary):
    """Detail-view representation, including related evidence and audit events."""

    evidence: list[EvidenceOut] = []
    audit_events: list[AuditEventOut] = []


class IncidentCreate(BaseModel):
    """Request body for creating a new incident."""

    title: str = Field(min_length=1, max_length=255)
    severity: Severity
    affected_service: str = Field(min_length=1, max_length=255)
    assigned_operator: str | None = Field(default=None, max_length=255)


class EvidenceCreate(BaseModel):
    """Request body for attaching evidence to an incident."""

    evidence_type: EvidenceType
    summary: str = Field(min_length=1)
    source: str | None = Field(default=None, max_length=255)
    payload: dict = Field(default_factory=dict)
