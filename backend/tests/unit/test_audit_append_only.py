"""Unit tests asserting the audit trail is append-only by design."""

from __future__ import annotations

import inspect

from app.domains.audit import repository as audit_repo


def test_audit_repository_exposes_no_mutation_functions() -> None:
    """The audit repository must not provide update/delete operations."""
    names = {
        name
        for name, obj in inspect.getmembers(audit_repo, inspect.isfunction)
    }
    forbidden = {"update_event", "delete_event", "update", "delete", "remove"}
    assert not (names & forbidden), f"unexpected mutation functions: {names & forbidden}"
    # Only append + read operations are provided.
    assert "append_event" in names
    assert "list_events_for_incident" in names
