"""Salesforce integration interface, fake adapter, and disabled REST skeleton.

SAFETY: The default adapter is FakeSalesforceIntegration, which makes NO
network calls and returns synthetic external IDs/URLs. The real
SalesforceRestIntegration stays disabled unless explicitly configured; it never
performs writes in the MVP.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from app.domains.incidents.models import Incident


@dataclass(frozen=True)
class SyncResult:
    """Result of a customer-impact sync attempt."""

    external_refs: dict
    succeeded: bool = True
    failure_reason: str | None = None


class SalesforceIntegration(Protocol):
    """Interface for syncing customer-impact data to Salesforce."""

    def sync_customer_impact(self, incident: Incident) -> SyncResult:
        ...


class FakeSalesforceIntegration:
    """Local, offline fake. Returns deterministic synthetic external references."""

    name = "fake"

    def sync_customer_impact(self, incident: Incident) -> SyncResult:
        # Deterministic pseudo-IDs derived from the incident id (synthetic).
        digest = hashlib.sha1(incident.id.encode()).hexdigest()[:12].upper()
        base = "https://example-fake-salesforce.invalid"
        return SyncResult(
            external_refs={
                "service_incident": {
                    "id": f"a00{digest[:9]}",
                    "url": f"{base}/ServiceIncident/a00{digest[:9]}",
                },
                "customer_impact": {
                    "id": f"a01{digest[:9]}",
                    "url": f"{base}/CustomerImpact/a01{digest[:9]}",
                },
                "case": {
                    "id": f"500{digest[:9]}",
                    "url": f"{base}/Case/500{digest[:9]}",
                },
                "note": "Synthetic fake Salesforce references. No real records created.",
            },
        )


class SalesforceNotConfigured(RuntimeError):
    """Raised when the real Salesforce integration is used without configuration."""


class SalesforceRestIntegration:
    """Skeleton for a real Salesforce REST integration.

    Disabled by default. Requires SALESFORCE_ENABLED=true plus instance URL and
    credentials. Performs no writes in the MVP — the actual REST calls are a
    documented extension point so the project never implies a live connection.
    """

    name = "salesforce_rest"

    def __init__(self) -> None:
        from app.core.config import get_settings

        settings = get_settings()
        if not settings.salesforce_enabled:
            raise SalesforceNotConfigured(
                "Salesforce integration is disabled. Set SALESFORCE_ENABLED=true "
                "and provide instance URL and credentials to enable it."
            )
        missing = [
            var
            for var in ("salesforce_instance_url", "salesforce_client_id", "salesforce_client_secret")
            if not getattr(settings, var, None)
        ]
        if missing:
            raise SalesforceNotConfigured(
                f"Salesforce configuration incomplete. Missing: {', '.join(missing)}."
            )

    def sync_customer_impact(self, incident: Incident) -> SyncResult:
        raise NotImplementedError(
            "SalesforceRestIntegration writes are not implemented in the MVP."
        )
