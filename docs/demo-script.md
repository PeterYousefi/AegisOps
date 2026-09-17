# AegisOps — Demo Script (2–3 minutes)

A concise, portfolio-ready walkthrough of the Checkout API incident story.

## Setup (before recording)

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:3000`.

## Script

**(0:00) Framing.**
"AegisOps is a human-governed AI incident-response tool for cloud operations.
Everything here uses synthetic data, every remediation is simulated, and a human
must approve any action. Let me walk through a real incident."

**(0:20) The dashboard.**
"Here's the incident dashboard. I can filter by status and severity. There's a
critical SEV1 on the Checkout API — elevated 5xx errors after a deploy. Let me
open it."

**(0:40) Evidence.**
"The detail page brings together everything in one place: an alert on the 5xx
error ratio, a metric showing the spike, application logs showing payment-
provider timeouts, and the deployment that landed a minute before the spike.
This is the evidence the AI is allowed to reason over — nothing else."

**(1:05) AI assessment.**
"I run AI analysis. The assessment is evidence-grounded: it identifies the likely
root cause — a deploy that lowered the payment client timeout — with 85%
confidence, and every claim cites specific evidence. These citations are
clickable; clicking one scrolls right to the underlying evidence. Crucially, the
AI output is validated against a strict schema and can only cite IDs that exist —
if it hallucinated, we'd show a safe fallback instead."

**(1:35) Proposal and approval.**
"It proposes a remediation: roll back the deployment. I can see the risk,
blast radius, prerequisites, rollback plan, and expected outcome. Nothing runs
automatically — I approve it as a human, with an optional comment."

**(2:00) Simulated remediation.**
"Now I run the remediation. It's simulated — no real system is touched — and the
incident moves to mitigated. If it had failed, the incident would return to
investigating with the failure recorded."

**(2:20) Report, sync, and audit.**
"I generate a post-incident report — timeline, customer impact, root cause,
follow-ups. Optionally I sync a customer-impact record to a fake Salesforce,
which returns synthetic IDs. And the whole thing is captured in an append-only
audit timeline: requested, generated, proposed, approved, started, completed."

**(2:45) Close.**
"So: evidence-grounded AI, strict validation, human approval, simulated-only
action, and a complete audit trail — an operational workflow, not a chatbot.
Thanks for watching."

## Reset between runs

```bash
docker compose down -v && docker compose up --build
```
