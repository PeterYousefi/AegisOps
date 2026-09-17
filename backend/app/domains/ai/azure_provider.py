"""Azure AI provider skeleton.

Configurable ONLY through environment variables. It raises a clear error when
configuration is incomplete and performs no network calls in the MVP — the
actual client wiring is intentionally left as a documented extension point so
the project never implies a live, configured service.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.domains.ai.provider import IncidentContext


class AzureProviderNotConfigured(RuntimeError):
    """Raised when AzureAIProvider is used without complete configuration."""


class AzureAIProvider:
    """AIProvider backed by Azure OpenAI / Azure AI Foundry (skeleton).

    Requires AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION, and AZURE_OPENAI_API_KEY to be set. When any are
    missing, construction fails with a clear message. No network call is made
    in the MVP.
    """

    name = "azure"

    REQUIRED_VARS = (
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_API_KEY",
    )

    def __init__(self) -> None:
        settings = get_settings()
        missing = [
            name
            for name in self.REQUIRED_VARS
            if not getattr(settings, name.lower(), None)
        ]
        if missing:
            raise AzureProviderNotConfigured(
                "AzureAIProvider is not configured. Missing environment "
                f"variables: {', '.join(missing)}. Set AI_PROVIDER=mock for "
                "local development, or provide the Azure configuration."
            )

    def _not_implemented(self) -> dict:
        raise NotImplementedError(
            "AzureAIProvider network calls are not implemented in the MVP. "
            "Wire the Azure OpenAI client here once the service is provisioned."
        )

    def generate_assessment(self, context: IncidentContext) -> dict:
        return self._not_implemented()

    def generate_proposal(self, context: IncidentContext) -> dict:
        return self._not_implemented()

    def generate_report(self, context: IncidentContext) -> dict:
        return self._not_implemented()
