# AegisOps — Implementation Task Plan (Phase 2)

Status: PROPOSED — awaiting approval of the first task. No application code is written until the user approves an individual task. Tasks are small, sequenced, and individually reviewable. Each task lists goal, files likely changed, dependencies, acceptance criteria, tests, and a verification command.

Ground rules carried into implementation:
- Implement only the one approved task at a time; then stop and wait for the next approval.
- No cloud provisioning, no real AI/Salesforce/GitHub credentials, no external-system writes.
- Every remediation is simulated. All AI output is validated. Audit is append-only.
- "Verified" means the verification command was actually run and observed.

AC-* references map to acceptance criteria in `requirements.md §7`.

---

## Milestone 1 — Local foundation

### T1.1 Repository scaffold, license, gitignore
- Goal: Create the top-level repo skeleton (directory tree, `LICENSE` MIT, `.gitignore`, root `.env.example` placeholders, empty domain folders with `__init__.py`), initialize git.
- Files: `LICENSE`, `.gitignore`, `.env.example`, `backend/app/**/__init__.py`, `frontend/` placeholder, `sample-data/`, `infra/`, `docs/` (already present), `.github/workflows/` dir.
- Dependencies: none.
- Acceptance: tree matches design §2; `.env.example` uses placeholders only (AC-2).
- Tests: none (structure only).
- Verify: `git status && grep -rIn "PLACEHOLDER\|example" .env.example && find . -maxdepth 2 -type d`.

### T1.2 Backend app factory, config, health endpoint
- Goal: FastAPI app factory (`main.py`), env-driven settings (`config.py` via pydantic-settings), `/health` route, structured JSON logging + correlation-id middleware skeleton, `pyproject.toml` with pinned deps + `requirements-pinned.txt`.
- Files: `backend/app/main.py`, `backend/app/config.py`, `backend/app/shared/{logging,correlation,errors}.py`, `backend/pyproject.toml`, `backend/requirements-pinned.txt`, `backend/.env.example`.
- Dependencies: T1.1.
- Acceptance: `GET /health` returns 200 JSON (AC-1, partial); no secrets hard-coded (AC-2).
- Tests: `tests/unit/test_health.py` (TestClient → 200 + JSON body).
- Verify: `cd backend && pip install -e . && pytest tests/unit/test_health.py -q`.

### T1.3 Frontend scaffold + typed API wrapper stub
- Goal: Next.js (App Router, TS strict, Tailwind) scaffold; `/` → `/incidents` redirect; typed API wrapper module + `types.ts` stub; base UI primitives; ESLint config.
- Files: `frontend/package.json`, `frontend/tsconfig.json`, `frontend/next.config.mjs`, `frontend/tailwind.config.ts`, `frontend/src/app/{layout,page,globals.css}`, `frontend/src/lib/api/client.ts`, `frontend/src/lib/types.ts`, `frontend/eslint.config.mjs`, `frontend/.env.example`.
- Dependencies: T1.1.
- Acceptance: lint + typecheck pass (AC-26).
- Tests: `tsc --noEmit`; ESLint.
- Verify: `cd frontend && npm ci && npm run lint && npx tsc --noEmit`.

### T1.4 Docker Compose (db + backend + frontend) + CI skeleton
- Goal: `docker-compose.yml` (postgres:16 with healthcheck, backend, frontend), backend + frontend `Dockerfile`, GitHub Actions `ci.yml` skeleton (jobs defined, deploy job disabled/manual placeholder).
- Files: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `.github/workflows/ci.yml`.
- Dependencies: T1.2, T1.3.
- Acceptance: `docker compose up` starts all three; `/health` reachable (AC-1); images build (AC-27, partial); CI file valid with disabled deploy job (AC-28, partial).
- Tests: none new (compose + build are the checks).
- Verify: `docker compose build && docker compose up -d && curl -fsS localhost:8000/health && docker compose down`.

---

## Milestone 2 — Database, migrations, seed data, incident APIs

### T2.1 Shared DB layer + enums + ORM models
- Goal: SQLAlchemy engine/session/Base (`shared/db.py`), enums (`shared/enums.py`), ORM models for all nine core tables + `post_incident_reports`.
- Files: `backend/app/shared/db.py`, `backend/app/shared/enums.py`, `backend/app/domains/*/models.py`.
- Dependencies: T1.2.
- Acceptance: models import cleanly; enums match design §3.2.
- Tests: `tests/unit/test_models_import.py` (metadata has expected tables).
- Verify: `cd backend && pytest tests/unit/test_models_import.py -q`.

### T2.2 Alembic init + first migration
- Goal: Alembic config + env; autogenerate/handwrite initial migration creating all tables + enum constraints + indexes.
- Files: `backend/alembic.ini`, `backend/migrations/env.py`, `backend/migrations/versions/0001_*.py`.
- Dependencies: T2.1.
- Acceptance: upgrade creates all nine core tables (+ reports) (AC-3).
- Tests: `tests/integration/test_migrations.py` (upgrade on ephemeral DB → introspect tables).
- Verify: `cd backend && alembic upgrade head && pytest tests/integration/test_migrations.py -q`.

### T2.3 Seed data (primary Checkout incident + 2 filler)
- Goal: Idempotent seed loading the primary Checkout API incident (≥1 alert, metric, log, deployment) + 3 runbooks (rows) + 2 filler incidents; runbook markdown files in `sample-data/runbooks/`.
- Files: `backend/seed/seed_data.py`, `sample-data/runbooks/{checkout-api-high-error-rate,payment-provider-timeout,rollback-procedure}.md`.
- Dependencies: T2.2.
- Acceptance: seed loads exactly the specified data (AC-4).
- Tests: `tests/integration/test_seed.py` (counts + presence of evidence types + 3 runbooks).
- Verify: `cd backend && python -m seed.seed_data && pytest tests/integration/test_seed.py -q`.

### T2.4 Incident + evidence + audit read APIs
- Goal: incidents router/service/repository (list with `?status=&severity=`, detail with nested relations), evidence list (`?type=`), audit read; incident state-machine service with invalid-transition rejection.
- Files: `backend/app/domains/incidents/*`, `backend/app/domains/evidence/*`, `backend/app/domains/audit/{repository,service,router}.py`.
- Dependencies: T2.3.
- Acceptance: filtering (AC-5); nested detail (AC-6); invalid transition rejected (AC-7).
- Tests: `tests/integration/test_incident_api.py`, `tests/unit/test_state_machine.py`.
- Verify: `cd backend && pytest tests/integration/test_incident_api.py tests/unit/test_state_machine.py -q`.

---

## Milestone 3 — Dashboard and incident detail UI

### T3.1 Incident list page + filters + states
- Goal: `/incidents` page rendering all required fields; status + severity filters; card/table responsive; loading/empty/error states; wired via typed API wrapper.
- Files: `frontend/src/app/incidents/page.tsx`, `frontend/src/components/incidents/*`, `frontend/src/components/ui/*`, `frontend/src/lib/api/*`.
- Dependencies: T2.4, T1.3.
- Acceptance: renders + filters + states (AC-8).
- Tests: component test for filters + empty/loading/error.
- Verify: `cd frontend && npm run lint && npx tsc --noEmit && npm test`.

### T3.2 Incident detail shell + evidence timeline/filters
- Goal: `/incidents/[id]` page shell with all section placeholders; evidence timeline with type filter; expandable items.
- Files: `frontend/src/app/incidents/[id]/page.tsx`, `frontend/src/components/evidence/*`.
- Dependencies: T3.1.
- Acceptance: sections render; evidence filtering works (AC-9, partial).
- Tests: component test for evidence filter.
- Verify: `cd frontend && npm run lint && npx tsc --noEmit && npm test`.

---

## Milestone 4 — Runbook retrieval and MockAIProvider

### T4.1 RunbookRetriever interface + keyword implementation
- Goal: `RunbookRetriever` interface + `KeywordRunbookRetriever` (keyword + metadata ranking, explainable score, matched terms); deterministic.
- Files: `backend/app/domains/runbooks/retrieval/*`.
- Dependencies: T2.3.
- Acceptance: deterministic ranked results with inspectable score (AC-11).
- Tests: `tests/unit/test_runbook_retrieval.py` (fixed input → identical ranked output).
- Verify: `cd backend && pytest tests/unit/test_runbook_retrieval.py -q`.

### T4.2 AIProvider interface + MockAIProvider + AI schemas
- Goal: strict Pydantic v2 schemas (assessment/proposal/report); `AIProvider` interface; deterministic `MockAIProvider` (positive + insufficient modes); `AzureAIProvider` skeleton (env-only, clear error, no network); composition root selection.
- Files: `backend/app/domains/ai/{schemas,provider,mock_provider,azure_provider,prompts}.py`, `backend/app/shared/container.py`.
- Dependencies: T4.1.
- Acceptance: mock returns schema-valid outputs (AC-12); insufficient mode populated (AC-13); Azure raises clear config error, no network (AC-15).
- Tests: `tests/unit/test_ai_schemas.py`, `tests/unit/test_mock_provider.py`, `tests/unit/test_azure_provider_config.py`.
- Verify: `cd backend && pytest tests/unit/test_ai_schemas.py tests/unit/test_mock_provider.py tests/unit/test_azure_provider_config.py -q`.

---

## Milestone 5 — AI assessment and evidence citations

### T5.1 Assessment workflow + validation pipeline + assess API
- Goal: workflow functions (`triage_incident`, `collect_relevant_evidence`, `retrieve_relevant_runbooks`, `generate_incident_assessment`); validation pipeline (schema + reference-existence); safe fallback; `POST /incidents/{id}/assess` + `GET .../assessment`; audit events.
- Files: `backend/app/domains/ai/{workflow,service}.py`, `backend/app/domains/ai/router.py`, audit integration.
- Dependencies: T4.2, T2.4.
- Acceptance: invalid-reference output rejected → fallback + `assessment_validation_failed` (AC-14); valid → `assessment_generated`.
- Tests: `tests/unit/test_validation_pipeline.py`, `tests/integration/test_assess_api.py`.
- Verify: `cd backend && pytest tests/unit/test_validation_pipeline.py tests/integration/test_assess_api.py -q`.

### T5.2 Assessment UI + clickable citations
- Goal: assessment panel (summary, root cause, confidence meter, next steps, uncertainties, safety notes); citations link/scroll to evidence/runbook items.
- Files: `frontend/src/components/ai/*`, citation link component, detail page wiring.
- Dependencies: T5.1, T3.2.
- Acceptance: citations resolve to rendered elements (AC-10).
- Tests: component test asserting citation IDs resolve.
- Verify: `cd frontend && npm run lint && npx tsc --noEmit && npm test`.

---

## Milestone 6 — Remediation approval, simulation, and audit events

### T6.1 Proposal generation + API
- Goal: `generate_remediation_proposal` (schema-valid, `required_approval=true`); `POST /incidents/{id}/proposals` (pending; state → awaiting_approval); audit `remediation_proposed`, `approval_requested`.
- Files: `backend/app/domains/remediation/{schemas,service,router}.py`, proposal model wiring.
- Dependencies: T5.1.
- Acceptance: new proposal pending + required_approval true (AC-16).
- Tests: `tests/integration/test_proposal_api.py`.
- Verify: `cd backend && pytest tests/integration/test_proposal_api.py -q`.

### T6.2 Approve / reject flow + audit
- Goal: `POST /proposals/{id}/approve` and `/reject` (optional comment); approval advances state, rejection → investigating; audit events.
- Files: `backend/app/domains/approvals/*`.
- Dependencies: T6.1.
- Acceptance: approve records `remediation_approved` + advances; reject records `remediation_rejected` + returns to investigating (AC-17).
- Tests: `tests/integration/test_approval_flow.py`.
- Verify: `cd backend && pytest tests/integration/test_approval_flow.py -q`.

### T6.3 SimulatedRemediationExecutor + execute guard
- Goal: `RemediationExecutor` interface + `SimulatedRemediationExecutor` (rollback_deployment, disable_feature_flag, scale_service; local-only; predictable failure mode); `POST /proposals/{id}/execute` with approval guard; success → mitigated; failure → investigating (proposal + failed execution preserved); audit start/completed/failed.
- Files: `backend/app/domains/remediation/{executor,simulated_executor}.py`, execute route.
- Dependencies: T6.2.
- Acceptance: execute-without-approval blocked, no execution row (AC-18); success → mitigated (AC-19); failure mode, no external calls (AC-20).
- Tests: `tests/unit/test_simulated_executor.py`, `tests/integration/test_execute_flow.py`.
- Verify: `cd backend && pytest tests/unit/test_simulated_executor.py tests/integration/test_execute_flow.py -q`.

### T6.4 Append-only audit assertions + audit timeline UI
- Goal: confirm audit repo has no update/delete; audit timeline UI on detail page; execution status UI incl. failure banner; approval controls UI.
- Files: `backend/app/domains/audit/*` (review), `frontend/src/components/{audit,remediation}/*`.
- Dependencies: T6.3.
- Acceptance: no audit mutation API; mutation attempts fail (AC-21); full flow ordered audit set (AC-22).
- Tests: `tests/unit/test_audit_append_only.py`, `tests/integration/test_full_flow_audit.py`; FE component test.
- Verify: `cd backend && pytest tests/unit/test_audit_append_only.py tests/integration/test_full_flow_audit.py -q && cd ../frontend && npm test`.

---

## Milestone 7 — Post-incident report and fake Salesforce adapter

### T7.1 Post-incident report generation + API + UI
- Goal: `generate_post_incident_report` (schema-valid); `POST /incidents/{id}/report` gated to `mitigated`; `GET .../report`; audit `post_incident_report_generated`; report UI section.
- Files: `backend/app/domains/ai/*` (report path), report router, `frontend/src/components/report/*`.
- Dependencies: T6.4.
- Acceptance: blocked before mitigation, allowed after (AC-23).
- Tests: `tests/integration/test_report_api.py`; FE render test.
- Verify: `cd backend && pytest tests/integration/test_report_api.py -q`.

### T7.2 Fake Salesforce adapter + REST skeleton + sync API + UI
- Goal: `SalesforceIntegration` interface; `FakeSalesforceIntegration` (fake IDs/URLs); `SalesforceRestIntegration` disabled skeleton; `POST /incidents/{id}/salesforce-sync` + `GET .../integration-syncs`; sync audit events; Salesforce panel UI.
- Files: `backend/app/domains/integrations/salesforce/*`, sync router, `frontend/src/components/salesforce/*`.
- Dependencies: T7.1.
- Acceptance: fake sync returns fake refs + records requested/completed; REST skeleton disabled without config (AC-24).
- Tests: `tests/unit/test_fake_salesforce.py`, `tests/integration/test_salesforce_sync.py`.
- Verify: `cd backend && pytest tests/unit/test_fake_salesforce.py tests/integration/test_salesforce_sync.py -q`.

---

## Milestone 8 — Tests, CI/CD, docs, Docker production config, Azure Bicep

### T8.1 Test suite completion + coverage pass
- Goal: fill remaining backend unit/integration gaps; ensure deterministic; frontend test pass.
- Files: `backend/tests/**`, `frontend/src/__tests__/**`.
- Dependencies: M7 complete.
- Acceptance: backend suite green (AC-25); FE lint/typecheck/tests green (AC-26).
- Verify: `cd backend && pytest -q && cd ../frontend && npm run lint && npx tsc --noEmit && npm test`.

### T8.2 CI/CD workflow completion
- Goal: complete `ci.yml`: FE install/lint/typecheck, BE install/test, image build validation, disabled/manual Azure deploy job with placeholders.
- Files: `.github/workflows/ci.yml`.
- Dependencies: T8.1.
- Acceptance: workflow defines all gates; deploy job disabled/manual, placeholders only (AC-28).
- Verify: workflow lint (`actionlint` if available) + review; local reproduction of each job's commands.

### T8.3 Azure Bicep placeholders
- Goal: `infra/main.bicep` + modules for ACR, Container Apps env + 2 apps, Key Vault, Log Analytics, App Insights, Storage + Blob, PostgreSQL params, managed identity; `main.parameters.example.json`.
- Files: `infra/**`.
- Dependencies: none hard (can parallel).
- Acceptance: all placeholder resources present; no real Azure identifiers (AC-29).
- Verify: `az bicep build --file infra/main.bicep` if Azure CLI available (build only, no deploy) + secret/id scan; otherwise structural review + scan.

### T8.4 Documentation set + README
- Goal: complete `README.md` (all 20 sections), `docs/azure-deployment.md`, `docs/salesforce-integration.md`, `docs/demo-script.md`, `docs/interview-talking-points.md`, `docs/ai-development-process.md`; keep `architecture.md` current.
- Files: `README.md`, `docs/*`.
- Dependencies: features complete for truthful docs.
- Acceptance: docs describe actual implemented behavior (AC-30).
- Verify: docs review against implemented features + `.env.example`/secret scan.

---

## Milestone 9 — Optional real Azure deployment (GATED)

### T9.1 Azure deployment (only after explicit approval)
- Goal: provision + deploy to Azure per Bicep.
- Status: BLOCKED. Not started, not planned for execution, until the user explicitly approves. Requires real subscription, credentials, and incurs cost.
- Note: This task will be broken down further and re-confirmed at the time; nothing here authorizes any cloud action.

---

## Suggested execution order
M1 (T1.1→T1.4) → M2 (T2.1→T2.4) → M3 (T3.1→T3.2) → M4 (T4.1→T4.2) → M5 (T5.1→T5.2) → M6 (T6.1→T6.4) → M7 (T7.1→T7.2) → M8 (T8.1→T8.4). M9 only on explicit approval.

Recommended first task: **T1.1 — Repository scaffold, license, gitignore.**
