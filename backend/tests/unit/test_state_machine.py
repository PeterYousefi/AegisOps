"""Unit tests for the incident state machine."""

from __future__ import annotations

import pytest

from app.shared.enums import IncidentStatus
from app.shared.state_machine import (
    InvalidStateTransition,
    assert_transition,
    can_transition,
)


def test_valid_transitions() -> None:
    assert can_transition(IncidentStatus.DETECTED, IncidentStatus.INVESTIGATING)
    assert can_transition(
        IncidentStatus.INVESTIGATING, IncidentStatus.AWAITING_APPROVAL
    )
    assert can_transition(IncidentStatus.AWAITING_APPROVAL, IncidentStatus.MITIGATING)
    assert can_transition(IncidentStatus.MITIGATING, IncidentStatus.MITIGATED)
    assert can_transition(IncidentStatus.MITIGATING, IncidentStatus.INVESTIGATING)
    assert can_transition(IncidentStatus.MITIGATED, IncidentStatus.RESOLVED)


def test_invalid_transitions_rejected() -> None:
    assert not can_transition(IncidentStatus.DETECTED, IncidentStatus.MITIGATED)
    assert not can_transition(IncidentStatus.RESOLVED, IncidentStatus.INVESTIGATING)
    with pytest.raises(InvalidStateTransition):
        assert_transition(IncidentStatus.DETECTED, IncidentStatus.RESOLVED)
