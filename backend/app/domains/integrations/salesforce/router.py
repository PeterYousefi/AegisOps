"""HTTP routes for the (fake) Salesforce customer-impact sync."""

from __future__ import annotations

import datetime as _dt

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.domains.integrations.salesforce import service
from app.shared.db import get_db

router = APIRouter(prefix="/incidents", tags=["salesforce"])


class IntegrationSyncOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    integration: str
    sync_type: str
    status: str
    external_refs: dict
    failure_reason: str | None
    created_at: _dt.datetime


@router.post("/{incident_id}/salesforce-sync", response_model=IntegrationSyncOut)
def sync(incident_id: str, db: Session = Depends(get_db)) -> IntegrationSyncOut:
    result = service.sync_customer_impact(db, incident_id)
    return IntegrationSyncOut.model_validate(result)


@router.get("/{incident_id}/integration-syncs", response_model=list[IntegrationSyncOut])
def list_syncs(incident_id: str, db: Session = Depends(get_db)) -> list[IntegrationSyncOut]:
    return [IntegrationSyncOut.model_validate(s) for s in service.list_syncs(db, incident_id)]
