"""ORM model for the append-only audit trail.

Audit rows are written once and never updated or deleted. Enforcement of
append-only behavior lives in the audit repository (no update/delete methods)
and is documented as a portfolio demonstration rather than a compliance-
certified logging system.
"""

from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.shared.enums import ActorType, AuditEventType


class AuditEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single append-only audit event."""

    __tablename__ = "audit_events"

    incident_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_type: Mapped[AuditEventType] = mapped_column(
        Enum(AuditEventType, native_enum=False, length=48), nullable=False
    )
    actor_type: Mapped[ActorType] = mapped_column(
        Enum(ActorType, native_enum=False, length=16), nullable=False
    )
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    previous_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    new_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    event_metadata: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
