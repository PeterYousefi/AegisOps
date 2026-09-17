"""Integration tests for creating incidents and adding evidence. Requires PostgreSQL."""

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

API = "/api/v1"


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
    return TestClient(create_app(Settings(APP_ENV="local")))


def _audit_types(incident_id: str) -> list[str]:
    with get_sessionmaker()() as s:
        rows = s.scalars(
            select(AuditEvent.event_type).where(AuditEvent.incident_id == incident_id)
        ).all()
    return [r if isinstance(r, str) else r.value for r in rows]


def test_create_incident(client: TestClient) -> None:
    resp = client.post(
        f"{API}/incidents",
        json={
            "title": "Payments API timeouts",
            "severity": "sev2",
            "affected_service": "payments-api",
            "assigned_operator": "me@example.com",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "detected"
    assert body["severity"] == "sev2"
    assert "incident_created" in _audit_types(body["id"])

    # It shows up in the list.
    listed = client.get(f"{API}/incidents").json()
    assert any(i["id"] == body["id"] for i in listed)


def test_create_incident_validation(client: TestClient) -> None:
    # Missing title / bad severity -> 422.
    assert client.post(f"{API}/incidents", json={"severity": "sev2", "affected_service": "x"}).status_code == 422
    assert (
        client.post(
            f"{API}/incidents",
            json={"title": "t", "severity": "sev9", "affected_service": "x"},
        ).status_code
        == 422
    )


def test_add_evidence(client: TestClient) -> None:
    inc = client.post(
        f"{API}/incidents",
        json={"title": "t", "severity": "sev3", "affected_service": "svc"},
    ).json()
    resp = client.post(
        f"{API}/incidents/{inc['id']}/evidence",
        json={
            "evidence_type": "log",
            "summary": "error spike in logs",
            "source": "app-logs",
            "payload": {"count": 42},
        },
    )
    assert resp.status_code == 201
    assert resp.json()["evidence_type"] == "log"

    ev = client.get(f"{API}/incidents/{inc['id']}/evidence").json()
    assert len(ev) == 1
    assert "evidence_added" in _audit_types(inc["id"])


def test_add_evidence_unknown_incident(client: TestClient) -> None:
    resp = client.post(
        f"{API}/incidents/nope/evidence",
        json={"evidence_type": "log", "summary": "x"},
    )
    assert resp.status_code == 404
