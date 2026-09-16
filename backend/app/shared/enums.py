"""Shared enumerations for the AegisOps domain model.

These are the canonical value sets referenced by the ORM models and validated
throughout the application. They are string enums so they serialize cleanly to
JSON and store as human-readable values in the database.
"""

from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    """Incident severity levels."""

    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"


class IncidentStatus(str, Enum):
    """Lifecycle states for an incident."""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    AWAITING_APPROVAL = "awaiting_approval"
    MITIGATING = "mitigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


class EvidenceType(str, Enum):
    """Types of evidence attached to an incident."""

    ALERT = "alert"
    METRIC = "metric"
    LOG = "log"
    DEPLOYMENT = "deployment"
    RUNBOOK = "runbook"
    OPERATOR_NOTE = "operator_note"


class ProposalStatus(str, Enum):
    """Lifecycle states for a remediation proposal."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"


class ApprovalDecision(str, Enum):
    """Human decision on a remediation proposal."""

    APPROVED = "approved"
    REJECTED = "rejected"


class ExecutionStatus(str, Enum):
    """Status of a (simulated) remediation execution."""

    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ActionType(str, Enum):
    """Supported simulated remediation actions."""

    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    DISABLE_FEATURE_FLAG = "disable_feature_flag"
    SCALE_SERVICE = "scale_service"


class ValidationStatus(str, Enum):
    """Outcome of validating AI-generated content."""

    VALID = "valid"
    INVALID_FALLBACK = "invalid_fallback"


class RiskLevel(str, Enum):
    """Risk level of a remediation proposal."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActorType(str, Enum):
    """Who or what performed an audited action."""

    OPERATOR = "operator"
    SYSTEM = "system"
    AI = "ai"


class AuditEventType(str, Enum):
    """Types of append-only audit events."""

    INCIDENT_CREATED = "incident_created"
    EVIDENCE_ADDED = "evidence_added"
    ASSESSMENT_REQUESTED = "assessment_requested"
    ASSESSMENT_GENERATED = "assessment_generated"
    ASSESSMENT_VALIDATION_FAILED = "assessment_validation_failed"
    REMEDIATION_PROPOSED = "remediation_proposed"
    APPROVAL_REQUESTED = "approval_requested"
    REMEDIATION_APPROVED = "remediation_approved"
    REMEDIATION_REJECTED = "remediation_rejected"
    SIMULATED_REMEDIATION_STARTED = "simulated_remediation_started"
    SIMULATED_REMEDIATION_COMPLETED = "simulated_remediation_completed"
    SIMULATED_REMEDIATION_FAILED = "simulated_remediation_failed"
    POST_INCIDENT_REPORT_GENERATED = "post_incident_report_generated"
    SALESFORCE_SYNC_REQUESTED = "salesforce_sync_requested"
    SALESFORCE_SYNC_COMPLETED = "salesforce_sync_completed"
    SALESFORCE_SYNC_FAILED = "salesforce_sync_failed"


class IntegrationSyncStatus(str, Enum):
    """Status of an external integration sync attempt."""

    REQUESTED = "requested"
    COMPLETED = "completed"
    FAILED = "failed"
