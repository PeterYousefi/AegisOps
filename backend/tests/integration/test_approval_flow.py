"""Integration tests for the approve/reject flow (T6.2). Requires PostgreSQL."""

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


def _new_proposal(client: TestClient) -> str:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    return client.post(f"{API}/incidents/{PRIMARY}/proposals").json()["id"]


def test_approve_records_audit_and_marks_approved(client: TestClient) -> None:
    pid = _new_proposal(client)
    resp = client.post(f"{API}/proposals/{pid}/approve", json={"comment": "LGTM"})
    assert resp.status_code == 200
    assert resp.json()["decision"] == "approved"
    assert resp.json()["comment"] == "LGTM"

    proposals = client.get(f"{API}/incidents/{PRIMARY}/proposals").json()
    assert proposals[0]["status"] == "approved"
    assert "remediation_approved" in _audit_types(PRIMARY)


def test_reject_returns_incident_to_investigating(client: TestClient) -> None:
    pid = _new_proposal(client)
    resp = client.post(f"{API}/proposals/{pid}/reject", json={"comment": "too risky"})
    assert resp.status_code == 200
    assert resp.json()["decision"] == "rejected"

    detail = client.get(f"{API}/incidents/{PRIMARY}").json()
    assert detail["status"] == "investigating"
    assert "remediation_rejected" in _audit_types(PRIMARY)


def test_cannot_approve_twice(client: TestClient) -> None:
    pid = _new_proposal(client)
    client.post(f"{API}/proposals/{pid}/approve")
    resp = client.post(f"{API}/proposals/{pid}/approve")
    assert resp.status_code == 422
