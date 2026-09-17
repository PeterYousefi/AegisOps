"""Integration tests for remediation proposal generation (T6.1).

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


def test_proposal_is_pending_and_requires_approval(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    resp = client.post(f"{API}/incidents/{PRIMARY}/proposals")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "pending"
    assert body["required_approval"] is True
    assert body["action_type"] == "rollback_deployment"


def test_proposal_moves_incident_to_awaiting_approval(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    client.post(f"{API}/incidents/{PRIMARY}/proposals")
    detail = client.get(f"{API}/incidents/{PRIMARY}").json()
    assert detail["status"] == "awaiting_approval"
    types = _audit_types(PRIMARY)
    assert "remediation_proposed" in types
    assert "approval_requested" in types


def test_list_proposals(client: TestClient) -> None:
    client.post(f"{API}/incidents/{PRIMARY}/assess")
    client.post(f"{API}/incidents/{PRIMARY}/proposals")
    resp = client.get(f"{API}/incidents/{PRIMARY}/proposals")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
