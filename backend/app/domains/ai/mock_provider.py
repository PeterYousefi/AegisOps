"""Deterministic mock AI provider.

Produces realistic, schema-valid content for the demo without any network
access or credentials. Output is deterministic: the same context always yields
the same result, and it only ever cites evidence/runbook IDs present in the
provided context.

Two modes emerge naturally from the context:
- Sufficient evidence (a deployment + logs present): a confident rollback
  recommendation.
- Insufficient evidence (key evidence withheld): low confidence with populated
  uncertainties and no concrete remediation beyond investigation.
"""

from __future__ import annotations

from app.domains.ai.provider import IncidentContext


def _by_type(context: IncidentContext) -> dict[str, list]:
    grouped: dict[str, list] = {}
    for e in context.evidence:
        grouped.setdefault(e.evidence_type, []).append(e)
    return grouped


def _all_evidence_ids(context: IncidentContext) -> list[str]:
    return [e.id for e in context.evidence]


def _all_runbook_ids(context: IncidentContext) -> list[str]:
    return [r.id for r in context.runbooks]


def _has_sufficient_evidence(grouped: dict[str, list]) -> bool:
    # A confident root-cause + rollback story needs a deployment and a
    # corroborating signal (log or metric).
    return "deployment" in grouped and ("log" in grouped or "metric" in grouped)


class MockAIProvider:
    """Deterministic AIProvider implementation for local development and tests."""

    name = "mock"

    def generate_assessment(self, context: IncidentContext) -> dict:
        grouped = _by_type(context)
        evidence_refs = _all_evidence_ids(context)
        runbook_refs = _all_runbook_ids(context)

        if _has_sufficient_evidence(grouped):
            return {
                "executive_summary": (
                    f"{context.affected_service} is failing due to a recently "
                    "deployed release that reduced the payment client timeout, "
                    "causing payment-provider timeouts and elevated 5xx errors."
                ),
                "severity": "sev1",
                "affected_services": [context.affected_service],
                "likely_root_cause": (
                    "A recent deployment lowered the payment client timeout, "
                    "so payment-provider calls now time out under normal latency, "
                    "producing checkout 5xx errors."
                ),
                "confidence_score": 0.85,
                "evidence_references": evidence_refs,
                "runbook_references": runbook_refs,
                "recommended_next_steps": [
                    "Roll back the most recent checkout-api release.",
                    "Confirm the 5xx error ratio returns to baseline after rollback.",
                ],
                "uncertainties": [],
                "safety_notes": [
                    "Remediation must be reviewed and approved by a human before execution.",
                    "All remediation in this environment is simulated.",
                ],
            }

        # Insufficient-evidence mode.
        return {
            "executive_summary": (
                f"There are signs of a problem with {context.affected_service}, "
                "but the available evidence is insufficient to determine a root cause."
            ),
            "severity": "sev2",
            "affected_services": [context.affected_service],
            "likely_root_cause": "Undetermined — insufficient evidence.",
            "confidence_score": 0.2,
            "evidence_references": evidence_refs,
            "runbook_references": runbook_refs,
            "recommended_next_steps": [
                "Collect deployment history and application logs for the affected service.",
            ],
            "uncertainties": [
                "No deployment evidence is available to correlate with the onset.",
                "Root cause cannot be confirmed from the current evidence.",
            ],
            "safety_notes": [
                "Do not remediate until the root cause is better understood.",
                "All remediation in this environment is simulated and requires approval.",
            ],
        }

    def generate_proposal(self, context: IncidentContext) -> dict:
        evidence_refs = _all_evidence_ids(context)
        runbook_refs = _all_runbook_ids(context)
        return {
            "action_type": "rollback_deployment",
            "action_description": (
                f"Roll back {context.affected_service} to the last known-good "
                "release prior to the suspect deployment."
            ),
            "justification": (
                "The incident onset correlates with a recent deployment that changed "
                "payment client behavior; rolling back is the fastest low-risk mitigation."
            ),
            "risk_level": "medium",
            "blast_radius": (
                f"Affects only {context.affected_service}; no data changes. Rollback "
                "restores the previous, known-good behavior."
            ),
            "prerequisites": [
                "The previous known-good release artifact is available.",
                "A human operator approves the rollback.",
            ],
            "rollback_plan": (
                "If the rollback does not restore baseline behavior, roll forward to "
                "the current release and continue investigation."
            ),
            "expected_outcome": (
                "The 5xx error ratio returns to baseline and checkout succeeds again."
            ),
            "required_approval": True,
            "evidence_references": evidence_refs,
            "runbook_references": runbook_refs,
        }

    def generate_report(self, context: IncidentContext) -> dict:
        return {
            "timeline_summary": (
                "A new release was deployed, checkout 5xx errors spiked within minutes, "
                "the incident was investigated, a rollback was approved and simulated, "
                "and error rates returned to baseline."
            ),
            "customer_impact_summary": (
                "A subset of checkout attempts failed during the incident window; no "
                "customer data was affected."
            ),
            "root_cause_summary": (
                "A deployment reduced the payment client timeout, causing payment-provider "
                "timeouts and elevated checkout 5xx errors."
            ),
            "remediation_summary": (
                "The suspect release was rolled back (simulated) to the last known-good "
                "release, restoring normal checkout behavior."
            ),
            "follow_up_actions": [
                "Add a guardrail test for payment client timeout configuration.",
                "Add an alert on payment-provider timeout rate.",
            ],
            "lessons_learned": [
                "Timeout configuration changes should be treated as high-risk.",
                "Deployment-correlated error spikes should trigger fast rollback consideration.",
            ],
        }
