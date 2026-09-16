"""Health endpoint.

Exposes a minimal liveness check. The response intentionally contains only a
static status, the fixed service name, and the configured environment label.
It never exposes secrets, configuration values, package versions, stack
traces, or system internals.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.config import Settings, get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Safe, fixed-shape health response contract."""

    status: str
    service: str
    environment: str


def _settings_from(request: Request) -> Settings:
    """Return the settings configured for the running app.

    Uses the settings stored on ``app.state`` by the app factory, so that a
    ``create_app(settings=...)`` override (e.g. in tests) is authoritative.
    Falls back to the cached global settings if none were attached.
    """
    return getattr(request.app.state, "settings", None) or get_settings()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health(request: Request) -> HealthResponse:
    """Return a simple liveness status.

    The ``environment`` value comes from configuration (``APP_ENV``) rather
    than being hard-coded into the route.
    """
    settings = _settings_from(request)
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        environment=settings.app_env,
    )
