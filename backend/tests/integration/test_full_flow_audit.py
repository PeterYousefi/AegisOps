"""Integration test: the full demo flow produces the expected ordered audit set.

Requires PostgreSQL; auto-skips otherwise.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.exc import OperationalError

from alembic import command
from alembic.config import Config
from app.core.config import Settings
from app.domains.audit.models import AuditEvent
from app.main import create_app
from app.shared.db import build_database_url, get_sessionmaker
from seed import seed_data

API = "/api/v1"
PRIMARY = seed_data.PRIMARY_INCIDENT_ID


def _db_available() -> bool:
    try:
        with create_engine(build_database_url()).connect():
            return True
    except OperationalError:
        return False


pytestmark = pytest.mark.skipif(not _db_available(), reason="No PostgreSQL available")


@pytest.fixture()
def client() -> TestClient:
    cfg = Config("alembic.ini")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    seed_data.run()
    return TestClient(create_app(Settings(APP_ENV="local")))


def _audit_types(incident_id: str) -> list[str]:
    with get_sessionmaker()() as s:
        rows = s.scalars(
            select(AuditEvent.event_type)
            .where(AuditEvent.incident_id == incident_id)
            .order_by(AuditEvent.created_at)
        ).all()
    return [r if isinstance(r, str) else r.value for r in rows]


def test_happy_path_audit_sequence(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    pid = client.post(f"{API}/incidents/{PRIMARY}/proposals").json()["id"]
    client.post(f"{API}/proposals/{pid}/approve")
    client.post(f"{API}/proposals/{pid}/execute")

    types = _audit_types(PRIMARY)
    # Expected ordered subsequence of the happy path.
    expected = [
        "assessment_requested",
        "assessment_generated",
        "remediation_proposed",
        "approval_requested",
        "remediation_approved",
        "simulated_remediation_started",
        "simulated_remediation_completed",
    ]
    # Every expected event appears, in order (allowing other events between).
    it = iter(types)
    assert all(evt in it for evt in expected), f"got sequence: {types}"


def test_audit_rows_are_not_mutated_by_flow(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    with get_sessionmaker()() as s:
        first = s.scalars(
            select(AuditEvent).where(AuditEvent.incident_id == PRIMARY).order_by(
                AuditEvent.created_at
            )
        ).first()
        original_id = first.id
        original_type = first.event_type

    # Run more of the flow; earlier rows must be unchanged (append-only).
    pid = client.post(f"{API}/incidents/{PRIMARY}/proposals").json()["id"]
    client.post(f"{API}/proposals/{pid}/approve")

    with get_sessionmaker()() as s:
        same = s.get(AuditEvent, original_id)
        assert same is not None
        assert same.event_type == original_type
