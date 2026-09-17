"""Seed the AegisOps database with synthetic demo data.

Loads:
- Three runbooks from sample-data/runbooks/*.md (front-matter parsed for
  slug/title/keywords/tags).
- One fully-detailed primary Checkout API incident with alert, metric, log,
  and deployment evidence.
- Two simpler filler incidents so the dashboard looks realistic.

The seed is IDEMPOTENT: it uses stable primary keys and upserts, so running it
multiple times does not create duplicates. Synthetic data only — no real
customers, services, or credentials.

Run with:  python -m seed.seed_data
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.evidence.models import EvidenceRecord
from app.domains.incidents.models import Incident
from app.domains.runbooks.models import Runbook
from app.shared.db import get_sessionmaker
from app.shared.enums import EvidenceType, IncidentStatus, Severity

# Repo root -> sample-data/runbooks
RUNBOOKS_DIR = Path(__file__).resolve().parents[2] / "sample-data" / "runbooks"

# Stable IDs so later components (e.g. the mock AI provider) can reference
# known evidence/runbook/incident IDs deterministically.
PRIMARY_INCIDENT_ID = "11111111-1111-1111-1111-111111111111"
EV_ALERT_ID = "22222222-0000-0000-0000-000000000001"
EV_METRIC_ID = "22222222-0000-0000-0000-000000000002"
EV_LOG_ID = "22222222-0000-0000-0000-000000000003"
EV_DEPLOY_ID = "22222222-0000-0000-0000-000000000004"
FILLER_INCIDENT_1_ID = "33333333-0000-0000-0000-000000000001"
FILLER_INCIDENT_2_ID = "33333333-0000-0000-0000-000000000002"

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_front_matter(text: str) -> tuple[dict, str]:
    """Parse simple YAML-ish front matter without a YAML dependency.

    Supports `key: value` and `key: [a, b, c]` list syntax used by our runbooks.
    Returns (metadata, body).
    """
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    block = match.group(1)
    body = text[match.end():]
    meta: dict = {}
    for line in block.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            items = [i.strip() for i in raw[1:-1].split(",") if i.strip()]
            meta[key] = items
        else:
            meta[key] = raw
    return meta, body


def _now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def seed_runbooks(session: Session) -> None:
    """Load runbooks from markdown files, upserting by slug."""
    for path in sorted(RUNBOOKS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = _parse_front_matter(text)
        slug = meta.get("slug") or path.stem
        title = meta.get("title") or slug
        keywords = meta.get("keywords") or []
        tags = meta.get("tags") or []

        existing = session.scalar(select(Runbook).where(Runbook.slug == slug))
        if existing is None:
            session.add(
                Runbook(
                    slug=slug,
                    title=title,
                    content_markdown=body,
                    keywords=keywords,
                    tags=tags,
                )
            )
        else:
            existing.title = title
            existing.content_markdown = body
            existing.keywords = keywords
            existing.tags = tags


def _upsert_incident(session: Session, incident: Incident) -> None:
    existing = session.get(Incident, incident.id)
    if existing is None:
        session.add(incident)


def _upsert_evidence(session: Session, evidence: EvidenceRecord) -> None:
    existing = session.get(EvidenceRecord, evidence.id)
    if existing is None:
        session.add(evidence)


def seed_incidents(session: Session) -> None:
    """Load the primary Checkout incident + evidence and two filler incidents."""
    base = _now() - _dt.timedelta(minutes=30)

    # --- Primary Checkout API incident ---
    _upsert_incident(
        session,
        Incident(
            id=PRIMARY_INCIDENT_ID,
            reference="INC-1001",
            title="Checkout API elevated 5xx errors after deploy",
            severity=Severity.SEV1,
            status=IncidentStatus.INVESTIGATING,
            affected_service="checkout-api",
            assigned_operator="on-call-operator",
            ai_summary=None,
        ),
    )

    # Ensure the parent incident row exists before inserting its evidence
    # (satisfies the evidence -> incident foreign key).
    session.flush()

    _upsert_evidence(
        session,
        EvidenceRecord(
            id=EV_ALERT_ID,
            incident_id=PRIMARY_INCIDENT_ID,
            evidence_type=EvidenceType.ALERT,
            source="monitoring",
            summary="Alert: Checkout API 5xx error ratio exceeded 5% over 5 minutes.",
            payload={
                "alert_name": "checkout-api-5xx-high",
                "threshold": "5% over 5m",
                "observed": "12.4%",
                "service": "checkout-api",
            },
            observed_at=base,
        ),
    )
    _upsert_evidence(
        session,
        EvidenceRecord(
            id=EV_METRIC_ID,
            incident_id=PRIMARY_INCIDENT_ID,
            evidence_type=EvidenceType.METRIC,
            source="metrics",
            summary="Error-rate metric spiked from ~0.3% to ~12% shortly after 14:02 UTC.",
            payload={
                "metric": "http_5xx_ratio",
                "baseline": 0.003,
                "peak": 0.124,
                "unit": "ratio",
            },
            observed_at=base + _dt.timedelta(minutes=2),
        ),
    )
    _upsert_evidence(
        session,
        EvidenceRecord(
            id=EV_LOG_ID,
            incident_id=PRIMARY_INCIDENT_ID,
            evidence_type=EvidenceType.LOG,
            source="application-logs",
            summary="Repeated payment-provider timeout errors in checkout-api logs.",
            payload={
                "signature": "PaymentProviderTimeoutError",
                "count_5m": 842,
                "example": "upstream payment provider timed out after 2000ms",
            },
            observed_at=base + _dt.timedelta(minutes=3),
        ),
    )
    _upsert_evidence(
        session,
        EvidenceRecord(
            id=EV_DEPLOY_ID,
            incident_id=PRIMARY_INCIDENT_ID,
            evidence_type=EvidenceType.DEPLOYMENT,
            source="deployment-history",
            summary="Release checkout-api@2026.09.15-3 deployed at 14:01 UTC, ~1 minute before the spike.",
            payload={
                "release": "checkout-api@2026.09.15-3",
                "previous_release": "checkout-api@2026.09.15-2",
                "deployed_at": "2026-09-15T14:01:00Z",
                "change_summary": "reduced payment client timeout from 5000ms to 2000ms",
            },
            observed_at=base - _dt.timedelta(minutes=1),
        ),
    )

    # --- Additional incidents for a realistic, populated dashboard ---
    _upsert_incident(
        session,
        Incident(
            id=FILLER_INCIDENT_1_ID,
            reference="INC-1002",
            title="Search service elevated latency",
            severity=Severity.SEV3,
            status=IncidentStatus.MITIGATED,
            affected_service="search-api",
            assigned_operator="on-call-operator",
            ai_summary="Latency returned to baseline after cache warmup.",
        ),
    )
    _upsert_incident(
        session,
        Incident(
            id=FILLER_INCIDENT_2_ID,
            reference="INC-1003",
            title="Image CDN cache miss rate elevated",
            severity=Severity.SEV4,
            status=IncidentStatus.DETECTED,
            affected_service="cdn",
            assigned_operator=None,
            ai_summary=None,
        ),
    )
    _upsert_incident(
        session,
        Incident(
            id="33333333-0000-0000-0000-000000000003",
            reference="INC-1004",
            title="Auth service token validation failures",
            severity=Severity.SEV2,
            status=IncidentStatus.AWAITING_APPROVAL,
            affected_service="auth-api",
            assigned_operator="on-call-operator",
            ai_summary="Elevated 401s traced to a clock-skew issue on a new node.",
        ),
    )
    _upsert_incident(
        session,
        Incident(
            id="33333333-0000-0000-0000-000000000004",
            reference="INC-1005",
            title="Orders database connection pool exhaustion",
            severity=Severity.SEV2,
            status=IncidentStatus.INVESTIGATING,
            affected_service="orders-api",
            assigned_operator="on-call-operator",
            ai_summary=None,
        ),
    )
    _upsert_incident(
        session,
        Incident(
            id="33333333-0000-0000-0000-000000000005",
            reference="INC-1006",
            title="Notification worker queue backlog",
            severity=Severity.SEV3,
            status=IncidentStatus.RESOLVED,
            affected_service="notifications",
            assigned_operator="on-call-operator",
            ai_summary="Backlog cleared after scaling workers; no customer impact.",
        ),
    )


def run() -> None:
    """Seed the database idempotently."""
    session_factory = get_sessionmaker()
    with session_factory() as session:
        seed_runbooks(session)
        seed_incidents(session)
        session.commit()


if __name__ == "__main__":
    run()
