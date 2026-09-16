---
slug: rollback-procedure
title: Safe Deployment Rollback Procedure
tags: [rollback, deployment, remediation, release, safe]
keywords: [rollback, deployment, revert, previous release, redeploy, mitigation, safe rollback]
---

# Safe Deployment Rollback Procedure

## Summary

Use this runbook to safely roll back a deployment that introduced a regression.
Rolling back to the last known-good release is often the fastest, lowest-risk
mitigation for an incident caused by a recent change.

## Prerequisites

- The incident is correlated with a specific recent deployment.
- The previous known-good release artifact is available.
- A human operator has approved the rollback.

## Rollback steps (conceptual)

1. Identify the last known-good release preceding the suspect deployment.
2. Announce the rollback to stakeholders.
3. Re-deploy the known-good release using the standard deployment pipeline.
4. Monitor the error-rate and latency metrics until they return to baseline.
5. Confirm the incident's symptoms have cleared before declaring mitigation.

## Verification

- The 5xx error ratio returns to its normal baseline.
- Checkout latency returns to expected levels.
- No new error signatures appear in the logs after the rollback.

## Rollback safety notes

- Rollback should be reversible: keep the ability to roll forward again.
- Prefer rollback over ad-hoc hotfixes during an active incident.
- Record the rollback and its outcome in the incident audit trail.

## Related runbooks

- Checkout API High Error Rate (`checkout-api-high-error-rate`)
- Payment Provider Timeout (`payment-provider-timeout`)
