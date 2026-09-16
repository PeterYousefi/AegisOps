"""ORM model for external integration sync attempts (e.g. Salesforce)."""

from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.shared.enums import IntegrationSyncStatus


class IntegrationSync(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A record of an attempt to sync incident data to an external system."""

    __tablename__ = "integration_syncs"

    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    integration: Mapped[str] = mapped_column(String(64), nullable=False)
    sync_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[IntegrationSyncStatus] = mapped_column(
        Enum(IntegrationSyncStatus, native_enum=False, length=16), nullable=False
    )
    external_refs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
