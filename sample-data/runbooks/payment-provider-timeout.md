---
slug: payment-provider-timeout
title: Payment Provider Timeout / Dependency Failure
tags: [payment, dependency, timeout, checkout, downstream]
keywords: [payment provider, timeout, dependency failure, upstream, gateway, connection reset, latency]
---

# Payment Provider Timeout / Dependency Failure

## Summary

Use this runbook when the Checkout API is failing because calls to the payment
provider are timing out or returning errors. The Checkout service depends on the
payment provider to authorize transactions; when that dependency degrades,
checkout requests fail with 5xx responses.

## Detection

- Application logs show repeated payment-provider timeout or connection-reset
  errors.
- Checkout latency rises and the 5xx error ratio climbs.

## Investigation steps

1. Confirm the log signature: look for timeout, connection reset, or gateway
   errors referencing the payment provider.
2. Check whether a recent deployment changed the payment client configuration
   (timeouts, endpoints, retry policy, connection pool size).
3. Check the payment provider's own status; distinguish a provider outage from
   a change on our side.
4. Assess impact: which payment methods and what share of checkouts are failing.

## Likely causes

- A deployment reduced the client timeout or misconfigured the payment endpoint.
- Connection pool exhaustion under load.
- A genuine payment-provider degradation.

## Recommended actions

- If a recent release changed payment client behavior, roll it back (see the
  rollback procedure runbook).
- If a risky payment-related feature flag was enabled, disable it.
- If the provider itself is down, follow provider-outage communication steps and
  avoid customer-facing automated messaging.

## Related runbooks

- Checkout API High Error Rate (`checkout-api-high-error-rate`)
- Rollback Procedure (`rollback-procedure`)
