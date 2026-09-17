"""Manual customer-impact sync to Salesforce (fake by default)."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.domains.audit import service as audit_service
from app.domains.incidents import service as incident_service
from app.domains.integrations.salesforce.models import IntegrationSync
from app.shared.container import get_salesforce_integration
from app.shared.enums import AuditEventType, IntegrationSyncStatus


def sync_customer_impact(session: Session, incident_id: str) -> IntegrationSync:
    """Manually sync an incident's customer impact to Salesforce.

    Records a requested event, performs the (fake) sync, and records a
    completed or failed event. No real communications are ever sent.
    """
    incident = incident_service.get_incident_or_404(session, incident_id)
    integration = get_salesforce_integration()

    audit_service.record_event(
        session,
        incident_id,
        AuditEventType.SALESFORCE_SYNC_REQUESTED,
        metadata={"integration": integration.name},
    )

    try:
        result = integration.sync_customer_impact(incident)
    except Exception as exc:  # includes NotImplementedError / not-configured
        sync = IntegrationSync(
            incident_id=incident_id,
            integration=integration.name,
            sync_type="customer_impact",
            status=IntegrationSyncStatus.FAILED,
            external_refs={},
            failure_reason=str(exc),
        )
        session.add(sync)
        session.flush()
        audit_service.record_event(
            session,
            incident_id,
            AuditEventType.SALESFORCE_SYNC_FAILED,
            metadata={"sync_id": sync.id, "reason": str(exc)},
        )
        session.commit()
        return sync

    status = (
        IntegrationSyncStatus.COMPLETED
        if result.succeeded
        else IntegrationSyncStatus.FAILED
    )
    sync = IntegrationSync(
        incident_id=incident_id,
        integration=integration.name,
        sync_type="customer_impact",
        status=status,
        external_refs=result.external_refs,
        failure_reason=result.failure_reason,
    )
    session.add(sync)
    session.flush()

    audit_service.record_event(
        session,
        incident_id,
        AuditEventType.SALESFORCE_SYNC_COMPLETED
        if result.succeeded
        else AuditEventType.SALESFORCE_SYNC_FAILED,
        metadata={"sync_id": sync.id},
    )
    session.commit()
    return sync


def list_syncs(session: Session, incident_id: str) -> list[IntegrationSync]:
    stmt = (
        select(IntegrationSync)
        .where(IntegrationSync.incident_id == incident_id)
        .order_by(desc(IntegrationSync.created_at))
    )
    return list(session.scalars(stmt).all())
