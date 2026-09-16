"""Health endpoint.

Exposes a minimal liveness check. The response intentionally contains only a
static status, the fixed service name, and the configured environment label.
It never exposes secrets, configuration values, package versions, stack
traces, or system internals.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import Settings, get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Safe, fixed-shape health response contract."""

    status: str
    service: str
    environment: str


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Return a simple liveness status.

    The ``environment`` value comes from configuration (``APP_ENV``) rather
    than being hard-coded into the route.
    """
    settings: Settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        environment=settings.app_env,
    )
