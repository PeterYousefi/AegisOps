"""Unit tests for the AzureAIProvider configuration guard."""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.domains.ai import azure_provider as azure_module
from app.domains.ai.azure_provider import AzureAIProvider, AzureProviderNotConfigured


def test_azure_provider_raises_when_unconfigured(monkeypatch) -> None:
    # Force settings with no Azure configuration.
    monkeypatch.setattr(
        azure_module, "get_settings", lambda: Settings(AI_PROVIDER="azure")
    )
    with pytest.raises(AzureProviderNotConfigured) as exc:
        AzureAIProvider()
    # Clear, actionable message; names the missing variables.
    assert "AZURE_OPENAI_ENDPOINT" in str(exc.value)


def test_azure_provider_makes_no_network_call_when_unconfigured(monkeypatch) -> None:
    # Construction fails before any client/network usage could occur.
    monkeypatch.setattr(
        azure_module, "get_settings", lambda: Settings(AI_PROVIDER="azure")
    )
    with pytest.raises(AzureProviderNotConfigured):
        AzureAIProvider()
