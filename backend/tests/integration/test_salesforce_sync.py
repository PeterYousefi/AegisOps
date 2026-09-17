"""Integration tests for the fake Salesforce sync (T7.2). Requires PostgreSQL."""

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


def test_fake_sync_returns_refs_and_audits(client: TestClient) -> None:
    resp = client.post(f"{API}/incidents/{PRIMARY}/salesforce-sync")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert body["integration"] == "fake"
    assert "service_incident" in body["external_refs"]

    with get_sessionmaker()() as s:
        types = [
            (r if isinstance(r, str) else r.value)
            for r in s.scalars(
                select(AuditEvent.event_type).where(
                    AuditEvent.incident_id == PRIMARY
                )
            ).all()
        ]
    assert "salesforce_sync_requested" in types
    assert "salesforce_sync_completed" in types


def test_list_syncs(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/salesforce-sync")
    resp = client.get(f"{API}/incidents/{PRIMARY}/integration-syncs")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
