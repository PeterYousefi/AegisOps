---
slug: checkout-api-high-error-rate
title: Checkout API — High 5xx Error Rate
tags: [checkout, api, errors, 5xx, availability]
keywords: [checkout, 5xx, error rate, elevated errors, availability, latency, payment]
---

# Checkout API — High 5xx Error Rate

## Summary

Use this runbook when the Checkout API shows an elevated rate of HTTP 5xx
responses. Elevated checkout errors directly impact revenue and customer trust,
so treat sustained spikes as a high-severity incident.

## Detection

- Alerting fires when the 5xx error ratio for the Checkout API exceeds the
  configured threshold (for example, 5% over a 5-minute window).
- Corroborate with the service's error-rate and latency metrics.

## Investigation steps

1. Confirm the alert against the current error-rate metric; rule out a noisy
   single data point.
2. Check the deployment history for the Checkout API. A spike that begins
   shortly after a release strongly suggests the release is the cause.
3. Inspect recent application logs for repeated error signatures, especially
   dependency failures (payment provider, database, downstream services).
4. Determine the blast radius: percentage of checkout attempts affected and
   whether specific regions or payment methods are involved.

## Likely causes

- A recent deployment introduced a regression.
- A downstream dependency (such as the payment provider) is timing out or
  failing.
- A feature flag enabled risky behavior.

## Recommended actions

- If the spike correlates with a recent release, prefer rolling back that
  release (see the rollback procedure runbook).
- If a specific feature flag is implicated, disable it.
- Escalate if error rates continue after mitigation.

## Related runbooks

- Payment Provider Timeout (`payment-provider-timeout`)
- Rollback Procedure (`rollback-procedure`)
