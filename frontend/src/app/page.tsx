import Link from "next/link";
import {
  ShieldCheck,
  Search,
  FileCheck2,
  PlayCircle,
  ScrollText,
  ArrowRight,
} from "lucide-react";

const STEPS = [
  {
    icon: Search,
    title: "Investigate with evidence",
    body: "Alerts, metrics, logs, deployments, and runbooks in one place.",
  },
  {
    icon: ShieldCheck,
    title: "Evidence-grounded AI",
    body: "Assessments cite exact evidence. AI output is strictly validated.",
  },
  {
    icon: FileCheck2,
    title: "Human approval",
    body: "Every remediation requires an explicit human approve or reject.",
  },
  {
    icon: PlayCircle,
    title: "Simulated remediation",
    body: "Actions are simulated only — no real systems are ever touched.",
  },
  {
    icon: ScrollText,
    title: "Full audit trail",
    body: "Every meaningful event is recorded in an append-only timeline.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-accent" aria-hidden />
          <span className="text-lg font-semibold tracking-tight">AegisOps</span>
        </div>
        <Link
          href="/incidents"
          className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
        >
          Open dashboard <ArrowRight className="h-4 w-4" aria-hidden />
        </Link>
      </header>

      <section className="mx-auto max-w-3xl px-6 pb-4 pt-16 text-center">
        <span className="inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600">
          Human-Governed AI Incident Response
        </span>
        <h1 className="mt-5 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Investigate incidents with AI.
          <br />
          Keep humans in control.
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-600">
          AegisOps brings together the evidence for a cloud incident, produces an
          evidence-grounded assessment, proposes a safe fix, and requires a human
          to approve it — then simulates the action and records everything.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link
            href="/incidents"
            className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-white hover:bg-accent-hover"
          >
            View incidents <ArrowRight className="h-4 w-4" aria-hidden />
          </Link>
          <a
            href="https://github.com/PeterYousefi/AegisOps#readme"
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100"
          >
            How it works
          </a>
        </div>
        <p className="mt-4 text-xs text-slate-400">
          Runs on synthetic data. Every remediation is simulated — no real
          systems are contacted.
        </p>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-16">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {STEPS.map((s) => (
            <div key={s.title} className="card p-4">
              <s.icon className="h-5 w-5 text-accent" aria-hidden />
              <h3 className="mt-3 text-sm font-semibold text-slate-900">
                {s.title}
              </h3>
              <p className="mt-1 text-sm text-slate-600">{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="mx-auto max-w-5xl px-6 py-8 text-center text-sm text-slate-400">
        AegisOps — a portfolio demonstration. MIT licensed.
      </footer>
    </div>
  );
}
