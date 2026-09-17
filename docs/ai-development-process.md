# AegisOps — AI-Assisted Development Process

This project was built with the help of AI development tooling. This note is a
truthful account of how that assistance was used and where human ownership
remained.

## How AI tooling assisted

- **Planning:** drafting the requirements, design, and task breakdown for review.
- **Coding:** generating implementation code for well-scoped, individually
  approved tasks.
- **Reviews:** suggesting improvements and catching issues during iteration.
- **Test generation:** proposing unit and integration tests alongside features.

## What the human owned

- **Design decisions:** architecture (modular monolith), the safety model
  (untrusted AI, human approval, simulated-only remediation), the data model,
  and the API surface.
- **Review and acceptance:** every change was reviewed and approved before it was
  committed; commits and merges happened at explicit gates.
- **Testing and verification:** changes were verified against a real PostgreSQL
  database and the frontend build/test suite before being accepted; results were
  reported honestly, including failures that were then fixed.
- **Deployment validation:** cloud deployment is gated and not performed without
  explicit approval.

## Honesty and safety commitments

- No feature, test, deployment, security control, or integration is claimed to
  work unless it was actually implemented and verified.
- AI output in the product itself is treated as untrusted and strictly validated.
- The project uses synthetic data and simulated actions throughout the MVP.

## Why this matters

AI tooling accelerated the mechanical work — scaffolding, boilerplate, tests,
and drafts — while the engineering judgment, safety design, and verification
stayed with the developer. That division is the point: the tools help you move
faster, but you remain responsible for correctness, safety, and the decisions
that matter.
