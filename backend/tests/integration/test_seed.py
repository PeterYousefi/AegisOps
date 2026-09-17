"""Integration test: seed data loads the expected demo dataset idempotently.

Requires a live PostgreSQL (POSTGRES_* env). Auto-skips otherwise. The test
runs migrations to head, seeds, asserts the dataset, then seeds again to prove
idempotency (no duplicates).
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError

from alembic import command
from alembic.config import Config
from app.domains.evidence.models import EvidenceRecord
from app.domains.incidents.models import Incident
from app.domains.runbooks.models import Runbook
from app.shared.db import build_database_url, get_sessionmaker
from app.shared.enums import EvidenceType
from seed import seed_data


def _database_available() -> bool:
    try:
        engine = create_engine(build_database_url())
        with engine.connect():
            return True
    except OperationalError:
        return False


pytestmark = pytest.mark.skipif(
    not _database_available(),
    reason="No PostgreSQL database available (set POSTGRES_* to run).",
)


def _fresh_schema() -> None:
    cfg = Config("alembic.ini")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")


def test_seed_loads_primary_incident_and_runbooks() -> None:
    _fresh_schema()
    seed_data.run()

    session_factory = get_sessionmaker()
    with session_factory() as session:
        # Three runbooks.
        runbook_count = session.scalar(select(func.count()).select_from(Runbook))
        assert runbook_count == 3

        # Primary incident exists.
        primary = session.get(Incident, seed_data.PRIMARY_INCIDENT_ID)
        assert primary is not None
        assert primary.affected_service == "checkout-api"

        # Primary incident has at least one of each required evidence type.
        for evidence_type in (
            EvidenceType.ALERT,
            EvidenceType.METRIC,
            EvidenceType.LOG,
            EvidenceType.DEPLOYMENT,
        ):
            count = session.scalar(
                select(func.count())
                .select_from(EvidenceRecord)
                .where(
                    EvidenceRecord.incident_id == seed_data.PRIMARY_INCIDENT_ID,
                    EvidenceRecord.evidence_type == evidence_type,
                )
            )
            assert count >= 1, f"missing evidence type {evidence_type}"

        # Three incidents total (1 primary + 2 filler).
        incident_count = session.scalar(select(func.count()).select_from(Incident))
        assert incident_count == 6


def test_seed_is_idempotent() -> None:
    _fresh_schema()
    seed_data.run()
    seed_data.run()  # second run must not duplicate

    session_factory = get_sessionmaker()
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Runbook)) == 3
        assert session.scalar(select(func.count()).select_from(Incident)) == 6
        evidence_count = session.scalar(
            select(func.count())
            .select_from(EvidenceRecord)
            .where(EvidenceRecord.incident_id == seed_data.PRIMARY_INCIDENT_ID)
        )
        assert evidence_count == 4
