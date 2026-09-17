"""Unit tests for the SimulatedRemediationExecutor."""

from __future__ import annotations

from app.domains.remediation.executor import SimulatedRemediationExecutor
from app.shared.enums import ActionType


def test_success_outcome() -> None:
    out = SimulatedRemediationExecutor().execute(ActionType.ROLLBACK_DEPLOYMENT)
    assert out.succeeded is True
    assert out.result["simulated"] is True
    assert out.result["action"] == "rollback_deployment"
    assert out.failure_reason is None


def test_predictable_failure_mode() -> None:
    out = SimulatedRemediationExecutor().execute(
        ActionType.ROLLBACK_DEPLOYMENT, fail=True
    )
    assert out.succeeded is False
    assert out.failure_reason is not None
    # Even on failure, the result is marked simulated and no changes are made.
    assert out.result["simulated"] is True


def test_all_supported_actions_are_simulated() -> None:
    ex = SimulatedRemediationExecutor()
    for action in (
        ActionType.ROLLBACK_DEPLOYMENT,
        ActionType.DISABLE_FEATURE_FLAG,
        ActionType.SCALE_SERVICE,
    ):
        out = ex.execute(action)
        assert out.result["simulated"] is True
