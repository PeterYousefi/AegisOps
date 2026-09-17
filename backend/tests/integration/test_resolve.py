"""Integration test for the resolve action (mitigated -> resolved). Requires PostgreSQL."""

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


def test_resolve_requires_mitigated(client: TestClient) -> None:
    # Fresh incident is 'investigating' -> resolve is an invalid transition (409).
    resp = client.post(f"{API}/incidents/{PRIMARY}/resolve")
    assert resp.status_code == 409


def test_resolve_after_mitigation(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    pid = client.post(f"{API}/incidents/{PRIMARY}/proposals").json()["id"]
    client.post(f"{API}/proposals/{pid}/approve")
    client.post(f"{API}/proposals/{pid}/execute")
    # Now mitigated -> resolve.
    resp = client.post(f"{API}/incidents/{PRIMARY}/resolve")
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"
