"""ORM model for incidents."""

from __future__ import annotations

import datetime as _dt

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.db import Base, TimestampMixin, UUIDPrimaryKeyMixin, str_enum
from app.shared.enums import IncidentStatus, Severity


class Incident(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A cloud operations incident."""

    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[Severity] = mapped_column(
        str_enum(Severity, length=16), nullable=False
    )
    status: Mapped[IncidentStatus] = mapped_column(
        str_enum(IncidentStatus, length=32), nullable=False
    )
    affected_service: Mapped[str] = mapped_column(String(255), nullable=False)
    assigned_operator: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: _dt.datetime.now(_dt.timezone.utc),
        onupdate=lambda: _dt.datetime.now(_dt.timezone.utc),
    )
