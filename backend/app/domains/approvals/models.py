"""ORM model for remediation approvals (human decisions)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.db import Base, TimestampMixin, UUIDPrimaryKeyMixin, str_enum
from app.shared.enums import ActorType, ApprovalDecision


class RemediationApproval(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A human approve/reject decision on a remediation proposal."""

    __tablename__ = "remediation_approvals"

    proposal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("remediation_proposals.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    decision: Mapped[ApprovalDecision] = mapped_column(
        str_enum(ApprovalDecision, length=16), nullable=False
    )
    actor_type: Mapped[ActorType] = mapped_column(
        str_enum(ActorType, length=16), nullable=False
    )
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
