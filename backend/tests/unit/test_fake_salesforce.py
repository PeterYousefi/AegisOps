"""Unit tests for the fake Salesforce adapter and disabled REST skeleton."""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.domains.incidents.models import Incident
from app.domains.integrations.salesforce import integration as sf
from app.shared.enums import IncidentStatus, Severity


def _incident() -> Incident:
    return Incident(
        id="11111111-1111-1111-1111-111111111111",
        title="Checkout errors",
        severity=Severity.SEV1,
        status=IncidentStatus.MITIGATED,
        affected_service="checkout-api",
    )


def test_fake_returns_synthetic_refs() -> None:
    result = sf.FakeSalesforceIntegration().sync_customer_impact(_incident())
    assert result.succeeded is True
    refs = result.external_refs
    assert "service_incident" in refs
    assert "customer_impact" in refs
    assert "case" in refs
    # URLs point at a clearly non-real host.
    assert ".invalid" in refs["service_incident"]["url"]


def test_fake_is_deterministic() -> None:
    a = sf.FakeSalesforceIntegration().sync_customer_impact(_incident())
    b = sf.FakeSalesforceIntegration().sync_customer_impact(_incident())
    assert a.external_refs == b.external_refs


def test_rest_skeleton_disabled_without_config(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.core.config.get_settings",
        lambda: Settings(SALESFORCE_ENABLED=False),
    )
    with pytest.raises(sf.SalesforceNotConfigured):
        sf.SalesforceRestIntegration()
