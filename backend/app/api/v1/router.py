"""Aggregate router for API v1.

Individual feature routers are included here. For T1.2 only the health route
exists; future tasks add incidents, evidence, AI, remediation, etc.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import health

api_router = APIRouter()
api_router.include_router(health.router)
