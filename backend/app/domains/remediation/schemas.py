"""API response schemas for remediation proposals, approvals, and executions."""

from __future__ import annotations

import datetime as _dt

from pydantic import BaseModel, ConfigDict


class ProposalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    assessment_id: str | None
    action_type: str
    action_description: str
    justification: str
    risk_level: str
    blast_radius: str
    prerequisites: list[str]
    rollback_plan: str
    expected_outcome: str
    required_approval: bool
    evidence_references: list[str]
    runbook_references: list[str]
    status: str
    created_at: _dt.datetime


class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    decision: str
    actor_type: str
    actor_id: str
    comment: str | None
    created_at: _dt.datetime


class ExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    action_type: str
    status: str
    result: dict | None
    failure_reason: str | None
    started_at: _dt.datetime
    completed_at: _dt.datetime | None


class ApprovalRequest(BaseModel):
    """Body for approve/reject actions."""

    comment: str | None = None
