"""Aggregate import of all ORM models.

Importing this module ensures every model is registered on ``Base.metadata``.
Used by tests and (later) Alembic autogeneration so the full schema is visible
from a single import.
"""

from __future__ import annotations

from app.domains.ai.models import IncidentAssessment, PostIncidentReport
from app.domains.approvals.models import RemediationApproval
from app.domains.audit.models import AuditEvent
from app.domains.evidence.models import EvidenceRecord
from app.domains.incidents.models import Incident
from app.domains.integrations.salesforce.models import IntegrationSync
from app.domains.remediation.models import (
    RemediationExecution,
    RemediationProposal,
)
from app.domains.runbooks.models import Runbook

__all__ = [
    "Incident",
    "EvidenceRecord",
    "Runbook",
    "IncidentAssessment",
    "PostIncidentReport",
    "RemediationProposal",
    "RemediationExecution",
    "RemediationApproval",
    "AuditEvent",
    "IntegrationSync",
]
