# AegisOps

**Human-Governed AI Incident Response for Cloud Operations**

AegisOps is an Azure-ready, full-stack AI incident-response platform. It helps a
cloud operator investigate a simulated incident by bringing together alerts,
metrics, logs, deployment history, and operational runbooks; produces an
evidence-grounded assessment; proposes a safe remediation plan; requires a human
to approve or reject it; simulates the approved action; and records a complete
audit trail.

> This is an early scaffold. The full README (setup, demo walkthrough, Azure and
> Salesforce guidance, testing, and portfolio talking points) is produced in a
> later documentation task. See the design docs below.

## Status

Local-first MVP under incremental development. Uses **synthetic data only**.
Every remediation is **simulated** and requires **explicit human approval**.
No real Azure, Salesforce, email, or deployment systems are contacted by the
base MVP.

## Documentation

- Requirements: [`.kiro/specs/aegisops/requirements.md`](.kiro/specs/aegisops/requirements.md)
- Design: [`.kiro/specs/aegisops/design.md`](.kiro/specs/aegisops/design.md)
- Task plan: [`.kiro/specs/aegisops/tasks.md`](.kiro/specs/aegisops/tasks.md)
- Architecture: [`docs/architecture.md`](docs/architecture.md)

## Backend foundation

A minimal FastAPI backend now exists under `backend/` using an app-factory
pattern with typed configuration and a structured JSON logging baseline.

**Currently available endpoint:**

```text
GET /api/v1/health  ->  200 {"status":"ok","service":"aegisops-api","environment":"local"}
```

The `environment` value comes from the `APP_ENV` setting. No database, AI
provider, or external integration is wired yet (those are later tasks).

**Intended local run and test commands** (requires **Python 3.12+**;
dependencies are installed in a later task and are not required just to read
the code):

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"                 # or: pip install -r requirements-pinned.txt
pytest                                   # run the backend tests
uvicorn app.main:app --reload            # run the API locally on http://localhost:8000
```

`requirements-pinned.txt` pins the direct dependencies only. A fully resolved
transitive lock file will be generated later on Python 3.12 (e.g. via
`pip-compile` or `uv pip compile`) during the dependency/CI task.

## Repository layout

```
frontend/          # Next.js app (App Router, TypeScript, Tailwind) — to be scaffolded
backend/           # FastAPI modular monolith (Python 3.12) — domain packages
infra/             # Azure Bicep templates (placeholders only, not deployed)
docs/              # Architecture and project documentation
sample-data/       # Synthetic runbooks and incident fixtures
.github/workflows/ # CI/CD (added in a later task)
.kiro/             # Specs (requirements, design, tasks)
```

## License

[MIT](LICENSE)
