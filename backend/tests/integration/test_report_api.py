"""Integration tests for post-incident report generation (T7.1). Requires PostgreSQL."""

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


def _mitigate(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    pid = client.post(f"{API}/incidents/{PRIMARY}/proposals").json()["id"]
    client.post(f"{API}/proposals/{pid}/approve")
    client.post(f"{API}/proposals/{pid}/execute")


def test_report_blocked_before_mitigation(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    resp = client.post(f"{API}/incidents/{PRIMARY}/report")
    assert resp.status_code == 422


def test_report_allowed_after_mitigation(client: TestClient) -> None:
    _mitigate(client)
    resp = client.post(f"{API}/incidents/{PRIMARY}/report")
    assert resp.status_code == 200
    body = resp.json()
    assert body["root_cause_summary"]
    assert isinstance(body["follow_up_actions"], list)

    with get_sessionmaker()() as s:
        types = [
            (r if isinstance(r, str) else r.value)
            for r in s.scalars(
                select(AuditEvent.event_type).where(
                    AuditEvent.incident_id == PRIMARY
                )
            ).all()
        ]
    assert "post_incident_report_generated" in types


def test_get_report_after_generation(client: TestClient) -> None:
    _mitigate(client)
    client.post(f"{API}/incidents/{PRIMARY}/report")
    resp = client.get(f"{API}/incidents/{PRIMARY}/report")
    assert resp.status_code == 200
