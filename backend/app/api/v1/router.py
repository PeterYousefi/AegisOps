"""Aggregate router for API v1.

Individual feature routers are included here. For T1.2 only the health route
exists; future tasks add incidents, evidence, AI, remediation, etc.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import health
from app.domains.ai.router import router as ai_router
from app.domains.audit.router import router as audit_router
from app.domains.evidence.router import router as evidence_router
from app.domains.incidents.router import router as incidents_router
from app.domains.approvals.router import router as approvals_router
from app.domains.remediation.router import router as remediation_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(incidents_router)
api_router.include_router(evidence_router)
api_router.include_router(audit_router)
api_router.include_router(ai_router)
api_router.include_router(remediation_router)
api_router.include_router(approvals_router)
