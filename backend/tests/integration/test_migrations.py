"""Integration test: Alembic migrations create the full schema.

Requires a live PostgreSQL reachable via the POSTGRES_* environment settings
(as used by the app). Skipped automatically when no database is available, so
the unit-test suite still runs in environments without Postgres.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError

from alembic import command
from alembic.config import Config
from app.shared.db import build_database_url

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


def _database_available() -> bool:
    try:
        engine = create_engine(build_database_url())
        with engine.connect():
            return True
    except OperationalError:
        return False


@pytest.mark.skipif(
    not _database_available(),
    reason="No PostgreSQL database available (set POSTGRES_* to run).",
)
def test_migrations_create_all_tables() -> None:
    cfg = Config("alembic.ini")

    # Start from a clean schema, then upgrade to head.
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")

    engine = create_engine(build_database_url())
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    missing = EXPECTED_TABLES - tables
    assert not missing, f"migration did not create: {sorted(missing)}"
