"""Integration tests for the AI assessment endpoint and pipeline.

Requires PostgreSQL (POSTGRES_* env); auto-skips otherwise.
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
from app.main import create_app
from app.shared.db import build_database_url, get_sessionmaker
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


@pytest.fixture()
def client() -> TestClient:
    cfg = Config("alembic.ini")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    seed_data.run()
    return TestClient(create_app(Settings(APP_ENV="local")))


def _audit_types(incident_id: str) -> list[str]:
    with get_sessionmaker()() as session:
        rows = session.scalars(
            select(AuditEvent.event_type)
            .where(AuditEvent.incident_id == incident_id)
            .order_by(AuditEvent.created_at)
        ).all()
    return [r if isinstance(r, str) else r.value for r in rows]


def test_assess_generates_valid_assessment(client: TestClient) -> None:
    resp = client.post(f"{API}/incidents/{seed_data.PRIMARY_INCIDENT_ID}/assess")
    assert resp.status_code == 200
    body = resp.json()
    assert body["validation_status"] == "valid"
    assert body["confidence_score"] >= 0.7
    # Cites real seeded evidence IDs.
    assert len(body["evidence_references"]) > 0

    types = _audit_types(seed_data.PRIMARY_INCIDENT_ID)
    assert "assessment_requested" in types
    assert "assessment_generated" in types


def test_get_assessment_after_assess(client: TestClient) -> None:
    client.post(f"{API}/incidents/{seed_data.PRIMARY_INCIDENT_ID}/assess")
    resp = client.get(f"{API}/incidents/{seed_data.PRIMARY_INCIDENT_ID}/assessment")
    assert resp.status_code == 200


def test_assess_unknown_incident_404(client: TestClient) -> None:
    resp = client.post(f"{API}/incidents/nope/assess")
    assert resp.status_code == 404


def test_invalid_ai_output_falls_back_and_audits(client: TestClient, monkeypatch) -> None:
    # Force the provider to cite a non-existent evidence id.
    from app.domains.ai import service as ai_service

    class BadProvider:
        name = "bad"

        def generate_assessment(self, context):
            return {
                "executive_summary": "s",
                "severity": "sev1",
                "affected_services": ["checkout-api"],
                "likely_root_cause": "x",
                "confidence_score": 0.9,
                "evidence_references": ["evidence-that-does-not-exist"],
                "runbook_references": [],
                "recommended_next_steps": [],
                "uncertainties": [],
                "safety_notes": [],
            }

        def generate_proposal(self, context):  # pragma: no cover
            return {}

        def generate_report(self, context):  # pragma: no cover
            return {}

    monkeypatch.setattr(ai_service, "get_ai_provider", lambda: BadProvider())

    resp = client.post(f"{API}/incidents/{seed_data.PRIMARY_INCIDENT_ID}/assess")
    assert resp.status_code == 200
    body = resp.json()
    assert body["validation_status"] == "invalid_fallback"
    assert body["confidence_score"] == 0.0
    assert body["evidence_references"] == []

    types = _audit_types(seed_data.PRIMARY_INCIDENT_ID)
    assert "assessment_validation_failed" in types
