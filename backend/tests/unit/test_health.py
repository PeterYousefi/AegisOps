"""Tests for the T1.2 backend foundation: the health endpoint and config.

Covers only what T1.2 delivers:
1. GET /api/v1/health returns HTTP 200.
2. The response matches the expected safe contract.
3. The configured APP_ENV value appears in the response.
4. A non-existent route returns 404.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

API_PREFIX = "/api/v1"


def _client(app_env: str = "local") -> TestClient:
    """Build a TestClient with explicit settings (no reliance on env)."""
    settings = Settings(APP_ENV=app_env)
    return TestClient(create_app(settings))


def test_health_returns_200() -> None:
    client = _client()
    response = client.get(f"{API_PREFIX}/health")
    assert response.status_code == 200


def test_health_response_contract() -> None:
    client = _client()
    response = client.get(f"{API_PREFIX}/health")
    body = response.json()

    # Exact, minimal contract — no extra fields that could leak internals.
    assert set(body.keys()) == {"status", "service", "environment"}
    assert body["status"] == "ok"
    assert body["service"] == "aegisops-api"
    assert isinstance(body["environment"], str)


def test_health_reflects_configured_app_env() -> None:
    client = _client(app_env="staging-test")
    response = client.get(f"{API_PREFIX}/health")
    assert response.status_code == 200
    assert response.json()["environment"] == "staging-test"


def test_unknown_route_returns_404() -> None:
    client = _client()
    response = client.get(f"{API_PREFIX}/does-not-exist")
    assert response.status_code == 404
