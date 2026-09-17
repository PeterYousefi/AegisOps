"""Remediation executor interface and the simulated implementation.

SAFETY: Only a SimulatedRemediationExecutor exists. It never calls Azure,
Kubernetes, shell tools, Terraform, Salesforce, or any real API. It only
computes an in-memory result describing what a real action *would* do.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.shared.enums import ActionType


@dataclass(frozen=True)
class ExecutionOutcome:
    """Result of a simulated remediation."""

    succeeded: bool
    result: dict
    failure_reason: str | None = None


class RemediationExecutor(Protocol):
    """Interface for executing a remediation action."""

    def execute(self, action_type: ActionType, *, fail: bool = False) -> ExecutionOutcome:
        ...


# Human-readable descriptions of what each simulated action represents.
_ACTION_NARRATIVE = {
    ActionType.ROLLBACK_DEPLOYMENT: "Rolled back to the last known-good release (simulated).",
    ActionType.DISABLE_FEATURE_FLAG: "Disabled the implicated feature flag (simulated).",
    ActionType.SCALE_SERVICE: "Scaled the service to absorb load (simulated).",
}


class SimulatedRemediationExecutor:
    """Deterministic, side-effect-free remediation simulator."""

    def execute(
        self, action_type: ActionType, *, fail: bool = False
    ) -> ExecutionOutcome:
        """Simulate a remediation action.

        Args:
            action_type: which supported action to simulate.
            fail: when True, deterministically produce a failure outcome (used
                to exercise the failure path in tests/demos). No external
                system is contacted in either case.
        """
        if fail:
            return ExecutionOutcome(
                succeeded=False,
                result={"action": action_type.value, "simulated": True},
                failure_reason=(
                    f"Simulated failure while performing {action_type.value}; "
                    "no changes were made."
                ),
            )

        return ExecutionOutcome(
            succeeded=True,
            result={
                "action": action_type.value,
                "simulated": True,
                "narrative": _ACTION_NARRATIVE.get(
                    action_type, "Performed action (simulated)."
                ),
            },
        )
