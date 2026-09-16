"""ORM models for AI-generated artifacts: assessments and post-incident reports."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.db import Base, TimestampMixin, UUIDPrimaryKeyMixin, str_enum
from app.shared.enums import Severity, ValidationStatus


class IncidentAssessment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An AI-generated, validated assessment of an incident."""

    __tablename__ = "incident_assessments"

    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(
        str_enum(Severity, length=16), nullable=False
    )
    affected_services: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    likely_root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_references: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    runbook_references: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    recommended_next_steps: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    uncertainties: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    safety_notes: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    validation_status: Mapped[ValidationStatus] = mapped_column(
        str_enum(ValidationStatus, length=32), nullable=False
    )


class PostIncidentReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An AI-generated post-incident report, produced after mitigation."""

    __tablename__ = "post_incident_reports"

    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    timeline_summary: Mapped[str] = mapped_column(Text, nullable=False)
    customer_impact_summary: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause_summary: Mapped[str] = mapped_column(Text, nullable=False)
    remediation_summary: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    lessons_learned: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
