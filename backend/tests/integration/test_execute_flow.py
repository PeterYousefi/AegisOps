"""Integration tests for the simulated remediation execute flow (T6.3).

Requires PostgreSQL; auto-skips otherwise.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError

from alembic import command
from alembic.config import Config
from app.core.config import Settings
from app.domains.audit.models import AuditEvent
from app.domains.remediation.models import RemediationExecution
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


def _execution_count() -> int:
    with get_sessionmaker()() as s:
        return s.scalar(select(func.count()).select_from(RemediationExecution)) or 0


def _proposal(client: TestClient) -> str:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    return client.post(f"{API}/incidents/{PRIMARY}/proposals").json()["id"]


def test_execute_without_approval_is_blocked_and_creates_no_execution(
    client: TestClient,
) -> None:
    pid = _proposal(client)
    before = _execution_count()
    resp = client.post(f"{API}/proposals/{pid}/execute")
    assert resp.status_code == 422
    assert _execution_count() == before  # no execution row created


def test_successful_execution_mitigates_incident(client: TestClient) -> None:
    pid = _proposal(client)
    client.post(f"{API}/proposals/{pid}/approve")
    resp = client.post(f"{API}/proposals/{pid}/execute")
    assert resp.status_code == 200
    assert resp.json()["status"] == "succeeded"

    detail = client.get(f"{API}/incidents/{PRIMARY}").json()
    assert detail["status"] == "mitigated"
    types = _audit_types(PRIMARY)
    assert "simulated_remediation_started" in types
    assert "simulated_remediation_completed" in types


def test_failed_execution_returns_to_investigating(client: TestClient) -> None:
    pid = _proposal(client)
    client.post(f"{API}/proposals/{pid}/approve")
    resp = client.post(f"{API}/proposals/{pid}/execute", params={"fail": "true"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "failed"
    assert resp.json()["failure_reason"]

    detail = client.get(f"{API}/incidents/{PRIMARY}").json()
    assert detail["status"] == "investigating"
    types = _audit_types(PRIMARY)
    assert "simulated_remediation_started" in types
    assert "simulated_remediation_failed" in types
    # Proposal and failed execution are preserved.
    assert _execution_count() >= 1
