"""Incident state machine.

Defines the allowed transitions between incident statuses and a guard that
rejects invalid transitions. Business services call ``assert_transition``
before changing an incident's status so invalid changes never reach the DB.
"""

from __future__ import annotations

from app.shared.enums import IncidentStatus

# Allowed transitions: from-status -> set of permitted next statuses.
ALLOWED_TRANSITIONS: dict[IncidentStatus, set[IncidentStatus]] = {
    IncidentStatus.DETECTED: {IncidentStatus.INVESTIGATING},
    IncidentStatus.INVESTIGATING: {IncidentStatus.AWAITING_APPROVAL},
    IncidentStatus.AWAITING_APPROVAL: {
        IncidentStatus.MITIGATING,
        IncidentStatus.INVESTIGATING,  # proposal rejected
    },
    IncidentStatus.MITIGATING: {
        IncidentStatus.MITIGATED,  # simulated remediation succeeded
        IncidentStatus.INVESTIGATING,  # simulated remediation failed
    },
    IncidentStatus.MITIGATED: {
        IncidentStatus.RESOLVED,
        IncidentStatus.INVESTIGATING,  # reopened
    },
    IncidentStatus.RESOLVED: set(),
}


class InvalidStateTransition(Exception):
    """Raised when an incident status change is not permitted."""

    def __init__(self, current: IncidentStatus, target: IncidentStatus) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"Invalid incident state transition: {current.value} -> {target.value}"
        )


def can_transition(current: IncidentStatus, target: IncidentStatus) -> bool:
    """Return True if moving from ``current`` to ``target`` is allowed."""
    return target in ALLOWED_TRANSITIONS.get(current, set())


def assert_transition(current: IncidentStatus, target: IncidentStatus) -> None:
    """Raise InvalidStateTransition if the transition is not allowed."""
    if not can_transition(current, target):
        raise InvalidStateTransition(current, target)
