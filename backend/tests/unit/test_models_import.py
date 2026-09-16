"""Verify the ORM models register the full expected schema on Base.metadata.

Importing the aggregate models module must populate Base.metadata with every
core table. This does not require a live database connection.
"""

from __future__ import annotations

from app.shared import models  # noqa: F401  (import registers models)
from app.shared.db import Base

EXPECTED_TABLES = {
    "incidents",
    "evidence_records",
    "runbooks",
    "incident_assessments",
    "post_incident_reports",
    "remediation_proposals",
    "remediation_executions",
    "remediation_approvals",
    "audit_events",
    "integration_syncs",
}


def test_all_core_tables_registered() -> None:
    registered = set(Base.metadata.tables.keys())
    missing = EXPECTED_TABLES - registered
    assert not missing, f"missing tables: {sorted(missing)}"


def test_incident_columns_present() -> None:
    incidents = Base.metadata.tables["incidents"]
    cols = set(incidents.columns.keys())
    assert {
        "id",
        "title",
        "severity",
        "status",
        "affected_service",
        "assigned_operator",
        "ai_summary",
        "created_at",
        "updated_at",
    } <= cols


def test_audit_event_has_metadata_and_correlation_columns() -> None:
    audit = Base.metadata.tables["audit_events"]
    cols = set(audit.columns.keys())
    # The attribute is event_metadata but the column name is "metadata".
    assert "metadata" in cols
    assert "correlation_id" in cols
    assert "event_type" in cols
