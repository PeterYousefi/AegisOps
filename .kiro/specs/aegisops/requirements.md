# AegisOps — Requirements Specification (Phase 0, Approved)

**Human-Governed AI Incident Response for Cloud Operations**

Status: APPROVED. This document is the agreed source of truth for scope and acceptance. No application code is implied by this document.

Locked defaults (from approval):
- Seed data: 1 fully-detailed Checkout API incident + 2 simpler filler incidents. Only the primary supports the full demo.
- Simulated failure: return incident to `investigating`, preserve proposal + failed execution, emit `simulated_remediation_started` and `simulated_remediation_failed`, UI shows mitigation failed.
- License: MIT.
- Package managers: frontend `npm`; backend `pip` + pinned `pyproject.toml`.

---

## 1. Repository state summary

| Aspect | Finding |
|---|---|
| Workspace path | `/Users/ajdar/Desktop/AegisOps` |
| Contents | Empty at project start (no files, no hidden files, no subdirectories) |
| Git | Not initialized at project start |
| Starting point | Greenfield — nothing to migrate or reconcile |

---

## 2. Assumptions

**A. Environment & tooling**
1. Docker + Docker Compose, Node.js 20+, and Python 3.12 are available locally.
2. macOS is the primary dev environment.
3. Long-lived processes (dev servers, DB container) are run by the user; exact commands are provided but blocking servers are not launched automatically.

**B. Scope of the MVP**
4. "MVP" = fully working locally with synthetic data and the deterministic MockAIProvider. No real cloud, no real AI credentials, no real Salesforce required to run and demo.
5. Azure and Salesforce are design + disabled-code deliverables in the MVP, not live integrations.
6. A single mock operator identity is acceptable for the MVP; full authentication (Entra ID) is a documented future phase.
7. Exactly one primary seeded incident (Checkout API) drives the demo; two filler incidents make the list realistic.

**C. AI behavior**
8. MockAIProvider is the default and is deterministic; it does not call any network service.
9. AzureAIProvider is an interface + skeleton reading config from env vars, failing clearly when unconfigured; it is not verified against a live endpoint in the MVP.

**D. Data & persistence**
10. PostgreSQL (local container) is the datastore for the MVP; SQLite is not used, for production parity.
11. Runbooks live as markdown files in `sample-data/runbooks/` and as rows in the `runbooks` table (via seed) so AI citations reference stable runbook IDs.

**E. Process**
12. Phase gates are followed strictly, with a stop-and-wait for approval at the end of each phase and before each implementation task.
13. "Verified" means the command was actually run and the result observed; no claim of passing tests/builds/deploys without running them.

---

## 3. Risks & dependencies

| # | Risk / dependency | Impact | Mitigation |
|---|---|---|---|
| R1 | AI hallucinated evidence/runbook IDs/actions | Safety-critical | Strict Pydantic validation; reject non-existent IDs; safe fallback + audit; deterministic mock default |
| R2 | Accidental real remediation | Real infra changes | Only SimulatedRemediationExecutor; no Azure/K8s/shell/Terraform/Salesforce calls; approval gate |
| R3 | Secrets leaking to git/logs | Security incident | `.env.example` placeholders only; no real IDs; Key Vault + managed identity documented; no secret fields in logs |
| R4 | Scope creep | Never finishing | Tight MVP; milestone gating; adapter isolation |
| R5 | Azure/Salesforce partial builds claimed working | Trust/credibility | Those paths disabled by default; documented as un-provisioned |
| R6 | Frontend/backend contract drift | Runtime bugs | Single typed API wrapper; OpenAPI from FastAPI; integration tests |
| R7 | Append-only audit weakened by ORM | Governance story undermined | No update/delete on audit repo; DB guidance documented; tests assert append-only |
| R8 | Non-determinism in mock breaks CI | Flaky tests | Fixed seed; no random/timestamps in mock output path; snapshot assertions |
| D1 | Postgres available locally | Blocks backend | Provided via Docker Compose |
| D2 | Node + Python toolchains | Blocks build | Documented versions in README + CI |

---

## 4. User stories

### Operator (primary persona)
- US-1 See a list of incidents with severity, status, and affected service to triage.
- US-2 Filter incidents by status and severity to focus on critical open incidents.
- US-3 Open an incident and review all evidence (alerts, metrics, logs, deployments, runbooks) in one place.
- US-4 Run AI-assisted analysis for an evidence-grounded assessment quickly.
- US-5 See every AI claim cite the exact evidence and runbook used, to verify and trust it.
- US-6 See a remediation proposal with risk, blast radius, prerequisites, rollback plan, and expected outcome.
- US-7 Explicitly approve or reject the proposal (optional comment) so a human is always in control.
- US-8 Have approved remediation run only as a simulation so no real systems are touched.
- US-9 See incident status advance to "mitigated" after a successful simulation.
- US-10 See a complete, append-only audit timeline of who did what and when.
- US-11 Generate a post-incident report to close the loop and share learnings.
- US-12 Optionally sync a customer-impact record to a fake Salesforce without real communications.

### Reviewer / hiring manager (secondary persona)
- US-13 Clear docs, architecture diagram, and demo script to understand design and safety in minutes.
- US-14 Run the project locally with one command set and no paid credentials.

---

## 5. Requirements

### 5.1 Functional requirements (FR)

**Incidents**
- FR-1 Store incidents: id, title, severity (sev1–sev4), status (detected, investigating, awaiting_approval, mitigating, mitigated, resolved), affected_service, created_at, updated_at, assigned_operator (mock), optional ai_summary.
- FR-2 API to list incidents and filter by status and severity.
- FR-3 API to fetch a single incident with related evidence, assessment, proposal, approvals, executions, audit events, report, and integration syncs.
- FR-4 Enforce the incident state machine (§5.5) on all transitions; reject invalid transitions.

**Evidence**
- FR-5 Store evidence typed as alert, metric, log, deployment, runbook, operator_note — each with stable id, incident_id, type, timestamp, payload, human-readable summary.
- FR-6 Frontend renders an evidence timeline with filtering by type.
- FR-7 Every AI evidence citation is traceable/clickable to the underlying evidence item.

**Runbooks & retrieval**
- FR-8 Include at least three markdown runbooks: `checkout-api-high-error-rate.md`, `payment-provider-timeout.md`, `rollback-procedure.md`.
- FR-9 Deterministic runbook retrieval using keyword matching + metadata ranking with an explainable score, behind a `RunbookRetriever` interface.
- FR-10 The AI workflow receives only retrieved evidence and retrieved runbooks.

**AI workflow**
- FR-11 Explicit workflow functions: `triage_incident`, `collect_relevant_evidence`, `retrieve_relevant_runbooks`, `generate_incident_assessment`, `generate_remediation_proposal`, `generate_post_incident_report`.
- FR-12 An `AIProvider` interface with a mandatory deterministic `MockAIProvider` (default, no credentials) and an `AzureAIProvider` skeleton configured only via env vars.
- FR-13 Validate all AI output with strict Pydantic v2 schemas before display, storage, or action.
- FR-14 Reject AI output referencing evidence/runbook IDs not present in the DB.
- FR-15 On validation failure: do not use raw output; return a safe fallback; record `assessment_validation_failed`; do not leak secrets/raw sensitive output.
- FR-16 The real-provider prompt instructs: use only supplied evidence/runbooks; never invent IDs; state insufficiency; no real external execution; all remediation needs human approval; return JSON only; follow schema exactly.

**AI schemas** (strict Pydantic)
- FR-17 Incident assessment: executive_summary, severity, affected_services, likely_root_cause, confidence_score (0–1), evidence_references[], runbook_references[], recommended_next_steps, uncertainties, safety_notes.
- FR-18 Remediation proposal: action_type, action_description, justification, risk_level, blast_radius, prerequisites, rollback_plan, expected_outcome, required_approval (always true), evidence_references[], runbook_references[].
- FR-19 Post-incident report: timeline_summary, customer_impact_summary, root_cause_summary, remediation_summary, follow_up_actions, lessons_learned.

**Approval & remediation**
- FR-20 A remediation proposal begins as `pending`.
- FR-21 A mock operator can approve or reject with an optional comment.
- FR-22 Approval records `remediation_approved` and advances state; rejection records `remediation_rejected` and returns incident to `investigating`.
- FR-23 Remediation cannot execute without a prior explicit approval (enforced server-side).
- FR-24 Implement only a `SimulatedRemediationExecutor` supporting `rollback_deployment`, `disable_feature_flag`, `scale_service`.
- FR-25 The simulator never calls Azure/K8s/shell/Terraform/Salesforce/real APIs; updates only local demo data; appends execution events; sets incident to `mitigated` on success; supports a predictable failure mode.

**Audit**
- FR-26 Maintain an append-only `audit_events` table + API recording at minimum the listed event types.
- FR-27 Audit fields: id, timestamp, actor_type, actor_id, event_type, incident_id, previous_state, new_state, metadata, correlation_id.
- FR-28 The audit repository exposes no update or delete operations.

**Post-incident report**
- FR-29 A post-incident report is generatable only after mitigation and records `post_incident_report_generated`.

**Salesforce (optional, disabled by default)**
- FR-30 Define a `SalesforceIntegration` interface, a working `FakeSalesforceIntegration`, and a disabled-by-default `SalesforceRestIntegration` skeleton.
- FR-31 A manual `sync_customer_impact(incident_id)` creates/updates a fake Service Incident, Customer Impact record, and support Case, returning fake external IDs/URLs.
- FR-32 Every sync attempt records `salesforce_sync_requested` and either `salesforce_sync_completed` or `salesforce_sync_failed`. No real emails or mass communications.

**Frontend**
- FR-33 Incident list page (fields + filters + card/table + loading/empty/error states) and incident detail page (all sections).
- FR-34 Frontend calls the backend only through a single typed API wrapper.

### 5.2 Non-functional requirements (NFR)
- NFR-1 Local-first: full demo runs locally with `docker compose` and no paid credentials.
- NFR-2 Determinism: MockAIProvider and seed data produce repeatable outputs.
- NFR-3 Type safety: Python typed + Pydantic v2; TypeScript strict mode.
- NFR-4 Observability: structured JSON logging; OpenTelemetry-ready hooks; correlation IDs on requests and audit events.
- NFR-5 Testability: backend unit + API integration tests; frontend lint + type check (+ light component tests).
- NFR-6 Accessibility: responsive, keyboard-navigable UI with sensible ARIA and contrast.
- NFR-7 Maintainability: modular monolith, clear domain boundaries, adapter interfaces; explicit over clever; no unused abstractions.
- NFR-8 Portability: containerized frontend and backend; env-driven config; no hard-coded environment specifics.
- NFR-9 Documentation: README + docs set kept current with behavior.

### 5.3 Safety requirements (SR) — mandatory, permanent
- SR-1 Synthetic data only in the MVP.
- SR-2 No real production remediation, ever, in the codebase.
- SR-3 No Azure CLI / Terraform apply / Bicep deploy / kubectl / arbitrary shell / destructive DB / external writes without explicit user approval.
- SR-4 Base MVP touches no real Azure/Salesforce/email/Slack/deploy system.
- SR-5 Every remediation action is simulated.
- SR-6 Every remediation action requires explicit UI approval.
- SR-7 All AI output treated as untrusted.
- SR-8 All AI output validated by strict Pydantic before display/store/act.
- SR-9 AI may cite only evidence/runbook IDs that exist in the DB.
- SR-10 AI must state uncertainty when evidence is insufficient.
- SR-11 AI must never invent logs/metrics/deployments/customers/citations/URLs/facts/outcomes.
- SR-12 No hard-coded secrets or cloud identifiers anywhere.
- SR-13 `.env.example` files use safe placeholders only.
- SR-14 Key Vault + managed identity documented as the production secret strategy.
- SR-15 Append-only audit trail for all meaningful incident/approval events.
- SR-16 No claim that a feature/test/deploy/control/integration works unless actually implemented and verified.

### 5.4 Out of scope (MVP)
- Real Azure provisioning or deployment (Milestone 9, explicit approval only).
- Real Salesforce writes or live org connection.
- Real authentication/SSO (Entra ID) — designed and documented, not implemented; mock operator identity used.
- Real email/Slack/paging/notifications.
- Vector database / semantic search (interface allows it later; deterministic keyword retrieval in MVP).
- Multi-tenant / RBAC / org management.
- Real payment provider or real telemetry ingestion.
- Autonomous agents or tool-calling loops.
- Compliance certification of the audit log (documented as a portfolio demonstration).

### 5.5 Incident state machine
```
detected → investigating → awaiting_approval → mitigating → mitigated → resolved
```
- `investigating → awaiting_approval` when a remediation proposal is created.
- `awaiting_approval → investigating` on rejection.
- `awaiting_approval → mitigating` on approval + start of simulated remediation.
- `mitigating → mitigated` on successful simulation.
- `mitigating → investigating` on a simulated failure (proposal + failed execution preserved).
- `mitigated → resolved` as an operator action after the post-incident report.
- Invalid transitions are rejected server-side and produce no state change.

---

## 6. Smallest complete MVP

1. Local foundation: repo structure, Docker Compose (backend + Postgres + frontend), `.env.example` files, health endpoint.
2. Data + APIs: SQLAlchemy models + Alembic migrations; seed loading the Checkout API incident + 2 filler; incident list/detail APIs with filtering.
3. Dashboard: incident list (filters, states) + incident detail (evidence timeline, filters, sections) via a typed API wrapper.
4. Retrieval + MockAIProvider: deterministic runbook retrieval with explainable scoring; deterministic MockAIProvider producing valid assessment/proposal/report; positive + insufficient-evidence cases.
5. Assessment + citations: run assessment, validate strictly, reject bad IDs, render clickable citations; audit events.
6. Approval + simulated remediation + audit: proposal → approve/reject → simulated executor → state to mitigated; append-only audit timeline in UI; failure mode.
7. Post-incident report + fake Salesforce: generate report after mitigation; manual fake Salesforce sync with fake IDs/URLs and sync audit events.
8. Quality gates: backend unit + API tests, frontend lint/typecheck, Dockerfiles, GitHub Actions CI, Bicep placeholders, and full docs — all created, none deployed.

---

## 7. Testable acceptance criteria

**Foundation**
- AC-1 `docker compose up` starts backend, frontend, Postgres; `GET /health` returns 200 JSON. (curl)
- AC-2 `.env.example` files exist for frontend and backend with placeholders only; no real secrets or Azure/Salesforce identifiers. (grep)

**Data & APIs**
- AC-3 Migrations create all nine core tables. (Alembic upgrade + introspection)
- AC-4 Seed loads the Checkout API incident with ≥1 alert, ≥1 metric, ≥1 log, ≥1 deployment record, and 3 runbooks. (DB query in test)
- AC-5 `GET /incidents?status=&severity=` returns filtered results. (API test)
- AC-6 `GET /incidents/{id}` returns nested relations. (API test)
- AC-7 Invalid state transition is rejected; state unchanged. (unit test)

**Dashboard**
- AC-8 List page renders incidents; both filters work; loading/empty/error states present. (manual + component test)
- AC-9 Detail page renders every required section; evidence-type filtering works. (manual + component test)
- AC-10 Every AI citation links/scrolls to the cited evidence or runbook. (manual + test)

**Retrieval & AI**
- AC-11 Runbook retrieval returns deterministic, ranked, inspectable-score results; identical output across runs. (unit test)
- AC-12 MockAIProvider returns schema-valid assessment, proposal, report for the demo incident. (unit test)
- AC-13 MockAIProvider produces an insufficient-evidence result with populated `uncertainties` when evidence is withheld. (unit test)
- AC-14 AI output citing a non-existent ID is rejected; safe fallback returned; `assessment_validation_failed` recorded. (unit test)
- AC-15 AzureAIProvider raises a clear config error when env vars absent; makes no network call. (unit test)

**Approval & remediation**
- AC-16 A new proposal has status `pending` and `required_approval = true`. (unit/API test)
- AC-17 Approval records `remediation_approved` and advances state; rejection records `remediation_rejected` and returns to `investigating`. (API test)
- AC-18 Remediation without prior approval is rejected server-side; no execution row. (API test)
- AC-19 Successful simulated remediation appends execution events and sets incident to `mitigated`. (API/unit test)
- AC-20 Predictable failure mode produces a failed execution without touching any external system. (unit test)

**Audit**
- AC-21 Audit repository exposes no update/delete; mutation attempts fail. (unit test + inspection)
- AC-22 Full demo flow produces the expected ordered set of audit event types. (integration test)

**Post-incident & Salesforce**
- AC-23 Post-incident report generatable only after `mitigated`; records `post_incident_report_generated`. (API test)
- AC-24 `FakeSalesforceIntegration.sync_customer_impact` returns fake external IDs/URLs and records requested + completed; REST skeleton disabled without config. (unit test)

**Quality gates**
- AC-25 Backend test suite runs green locally. (pytest)
- AC-26 Frontend lint and TypeScript checks pass. (npm run lint / tsc)
- AC-27 Docker images for frontend and backend build successfully. (docker build)
- AC-28 CI defines frontend install/lint/typecheck, backend install/test, image build validation; Azure deploy job disabled/manual with placeholders. (workflow review + CI run)
- AC-29 Bicep templates define all required placeholder resources; no real Azure identifiers. (review + scan)
- AC-30 README and docs exist and describe actual implemented behavior. (docs review)
