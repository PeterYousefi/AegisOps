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
