"""FastAPI application factory for the AegisOps backend.

Builds the app, configures structured logging, applies CORS from settings,
attaches a correlation-id middleware, and mounts the versioned API router.

No database, AI provider, or external integration is wired here (out of scope
for T1.2). Startup logging records that the service started, at an appropriate
level, without exposing configuration values.
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, correlation_id_var, get_logger
from app.shared.errors import register_exception_handlers


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure a FastAPI application instance.

    Args:
        settings: Optional settings override (primarily for tests). When not
            provided, cached settings from the environment are used.
    """
    settings = settings or get_settings()

    configure_logging(settings.log_level)
    logger = get_logger("aegisops.startup")

    app = FastAPI(
        title="AegisOps API",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # Make the resolved settings authoritative for this app instance so routes
    # use the injected configuration (important for tests) rather than the
    # cached global settings.
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        """Attach a correlation id to each request for traceable logs.

        Uses an inbound ``X-Correlation-ID`` header when present, otherwise
        generates one. The value is exposed on the response and made available
        to log records via a contextvar. Request bodies, headers, and cookies
        are never logged here.
        """
        correlation_id = request.headers.get("X-Correlation-ID") or uuid.uuid4().hex
        token = correlation_id_var.set(correlation_id)
        try:
            response = await call_next(request)
        finally:
            correlation_id_var.reset(token)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Startup log: state that the service started and its environment label
    # only. Do not log secrets or other configuration values.
    logger.info(
        "AegisOps backend started (service=%s, environment=%s)",
        settings.service_name,
        settings.app_env,
    )

    return app


# Module-level app for ASGI servers (e.g. `uvicorn app.main:app`).
app = create_app()
