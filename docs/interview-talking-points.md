# AegisOps — Interview Talking Points

Concise answers to likely questions about the project's design and safety.

## Why a modular monolith?

One deployable backend with clear internal domain boundaries (incidents,
evidence, runbooks, ai, remediation, approvals, audit, integrations). It gives
the readability and separation of services without distributed-systems
overhead, and it runs locally with one `docker compose` command — ideal for a
portfolio demo. Adapter interfaces at the edges (AI, retrieval, executor,
storage, Salesforce) make it straightforward to extract a service or swap an
implementation later.

## Why human approval?

Remediation actions change systems and can affect customers. A human approval
gate keeps accountability with a person, prevents automated mistakes, and is the
honest posture for AI-assisted operations. In AegisOps, execution is refused
server-side unless a prior approval exists.

## How do you reduce hallucinated actions?

The AI only ever sees the incident's retrieved evidence and runbooks — never a
free-form context — and it is instructed to cite only supplied IDs. Every output
is validated: strict Pydantic schema parsing plus a reference-existence check
that rejects any evidence/runbook ID not in the database. Invalid output is
discarded in favor of a conservative fallback, and the failure is audited.

## How are AI outputs validated?

Three steps: (1) parse into a strict Pydantic model (`extra='forbid'`, bounded
`confidence_score`, enum-validated fields); (2) verify all cited IDs exist; (3)
on any failure, return a safe fallback that invents nothing and record an
`assessment_validation_failed` audit event. Raw model output is never stored or
surfaced as a normal result.

## How do you protect cloud credentials and secrets?

No secrets or cloud identifiers in source — `.env.example` uses placeholders.
The production strategy is Azure Key Vault plus a user-assigned managed identity
(no long-lived credentials in app config). CI would authenticate to Azure via
OIDC federated credentials. Logs never include bodies, headers, cookies, or
credentials.

## How would this scale?

The stateless backend scales horizontally behind Container Apps; PostgreSQL
scales vertically and with read replicas. Runbook retrieval sits behind an
interface, so a vector store can replace keyword matching without touching
callers. The AI provider is an interface, so model calls can be batched, cached,
or moved to a queue. The audit table is append-only and partitionable by time.

## What changes would be required for production?

Real authentication (Entra ID) and RBAC, a live AzureAIProvider with output
evaluation and rate limiting, real (sandbox-first) Salesforce integration,
DB-level append-only enforcement on the audit table, secret management via Key
Vault, provisioned observability, and a real (still human-approved) remediation
executor with strong guardrails.

## Why is remediation simulated?

Safety and honesty. The project's purpose is to demonstrate the workflow and
governance, not to touch real infrastructure. The `SimulatedRemediationExecutor`
makes no external calls; it only updates local demo state. This keeps the demo
reproducible and risk-free while still exercising the full approval → execution
→ audit path.

## Why use an integration adapter for Salesforce?

It isolates an external, changeable dependency behind a stable interface. The
fake adapter lets the whole flow run offline and deterministically; the real
adapter can be implemented and enabled later via configuration without changing
callers. It also keeps the safety property that external writes require explicit
enablement and human action.

## How would you evaluate model quality and safety?

Golden-set evaluation on curated incidents (does the assessment cite the right
evidence and reach the right root cause?); schema-validity and
reference-existence rates as hard gates; hallucination rate (cited-but-absent
IDs) tracked over time; human-approval and override rates as feedback; and
red-team prompts to confirm the validation pipeline catches malformed or
injected output.
