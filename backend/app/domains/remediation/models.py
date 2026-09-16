"""ORM models for remediation proposals and (simulated) executions."""

from __future__ import annotations

import datetime as _dt

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.shared.enums import ActionType, ExecutionStatus, ProposalStatus, RiskLevel


class RemediationProposal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A proposed remediation action requiring human approval."""

    __tablename__ = "remediation_proposals"

    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assessment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("incident_assessments.id", ondelete="SET NULL"), nullable=True
    )
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, native_enum=False, length=32), nullable=False
    )
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, native_enum=False, length=16), nullable=False
    )
    blast_radius: Mapped[str] = mapped_column(Text, nullable=False)
    prerequisites: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    rollback_plan: Mapped[str] = mapped_column(Text, nullable=False)
    expected_outcome: Mapped[str] = mapped_column(Text, nullable=False)
    required_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    evidence_references: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    runbook_references: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[ProposalStatus] = mapped_column(
        Enum(ProposalStatus, native_enum=False, length=32), nullable=False
    )


class RemediationExecution(UUIDPrimaryKeyMixin, Base):
    """A record of a simulated remediation execution."""

    __tablename__ = "remediation_executions"

    proposal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("remediation_proposals.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, native_enum=False, length=32), nullable=False
    )
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus, native_enum=False, length=16), nullable=False
    )
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[_dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: _dt.datetime.now(_dt.timezone.utc),
    )
    completed_at: Mapped[_dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
