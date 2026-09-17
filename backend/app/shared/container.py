"""Composition root: selects concrete adapters from configuration.

Keeps adapter selection in one place so services depend on interfaces, not
concrete implementations. Driven by environment settings.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.domains.ai.provider import AIProvider


def get_ai_provider() -> AIProvider:
    """Return the configured AI provider.

    Defaults to the deterministic MockAIProvider. Selecting "azure" constructs
    the AzureAIProvider, which raises a clear error if it is not fully
    configured.
    """
    settings = get_settings()
    provider = (settings.ai_provider or "mock").lower()

    if provider == "azure":
        from app.domains.ai.azure_provider import AzureAIProvider

        return AzureAIProvider()

    from app.domains.ai.mock_provider import MockAIProvider

    return MockAIProvider()


def get_salesforce_integration():
    """Return the configured Salesforce integration.

    Defaults to the offline FakeSalesforceIntegration. The real REST
    integration is used only when SALESFORCE_ENABLED=true and configured.
    """
    settings = get_settings()
    if settings.salesforce_enabled:
        from app.domains.integrations.salesforce.integration import (
            SalesforceRestIntegration,
        )

        return SalesforceRestIntegration()

    from app.domains.integrations.salesforce.integration import (
        FakeSalesforceIntegration,
    )

    return FakeSalesforceIntegration()
