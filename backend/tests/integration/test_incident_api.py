"""Integration tests for the incident/evidence/audit read APIs.

Requires PostgreSQL (POSTGRES_* env); auto-skips otherwise. Migrates + seeds
a fresh schema, then exercises the endpoints via the FastAPI TestClient.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from alembic import command
from alembic.config import Config
from app.core.config import Settings
from app.main import create_app
from app.shared.db import build_database_url
from seed import seed_data

API = "/api/v1"


def _database_available() -> bool:
    try:
        engine = create_engine(build_database_url())
        with engine.connect():
            return True
    except OperationalError:
        return False


pytestmark = pytest.mark.skipif(
    not _database_available(),
    reason="No PostgreSQL database available (set POSTGRES_* to run).",
)


@pytest.fixture(scope="module")
def client() -> TestClient:
    cfg = Config("alembic.ini")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    seed_data.run()
    return TestClient(create_app(Settings(APP_ENV="local")))


def test_list_incidents_returns_all(client: TestClient) -> None:
    resp = client.get(f"{API}/incidents")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 6


def test_list_incidents_filter_by_status(client: TestClient) -> None:
    resp = client.get(f"{API}/incidents", params={"status": "investigating"})
    assert resp.status_code == 200
    body = resp.json()
    assert all(i["status"] == "investigating" for i in body)
    assert any(i["affected_service"] == "checkout-api" for i in body)


def test_list_incidents_filter_by_severity(client: TestClient) -> None:
    resp = client.get(f"{API}/incidents", params={"severity": "sev1"})
    assert resp.status_code == 200
    body = resp.json()
    assert all(i["severity"] == "sev1" for i in body)
    assert len(body) == 1


def test_incident_detail_includes_evidence(client: TestClient) -> None:
    resp = client.get(f"{API}/incidents/{seed_data.PRIMARY_INCIDENT_ID}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == seed_data.PRIMARY_INCIDENT_ID
    assert len(body["evidence"]) == 4
    assert "audit_events" in body


def test_incident_detail_404(client: TestClient) -> None:
    resp = client.get(f"{API}/incidents/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


def test_evidence_filter_by_type(client: TestClient) -> None:
    resp = client.get(
        f"{API}/incidents/{seed_data.PRIMARY_INCIDENT_ID}/evidence",
        params={"type": "alert"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["evidence_type"] == "alert"


def test_audit_endpoint_ok(client: TestClient) -> None:
    resp = client.get(f"{API}/incidents/{seed_data.PRIMARY_INCIDENT_ID}/audit")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
