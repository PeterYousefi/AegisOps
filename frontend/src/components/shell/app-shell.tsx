import Link from "next/link";
import { ShieldCheck, ListChecks, BookOpen } from "lucide-react";

/**
 * Application shell: a left sidebar with the AegisOps brand and navigation,
 * and a top bar. Wraps the operator-facing pages so the product reads as a
 * real console rather than a bare page.
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 shrink-0 flex-col border-r border-slate-200 bg-white sm:flex">
        <div className="flex items-center gap-2 px-5 py-4">
          <ShieldCheck className="h-6 w-6 text-accent" aria-hidden />
          <span className="text-lg font-semibold tracking-tight">AegisOps</span>
        </div>
        <nav className="flex flex-col gap-1 px-3 py-2 text-sm">
          <Link
            href="/incidents"
            className="flex items-center gap-2 rounded-lg px-3 py-2 font-medium text-slate-700 hover:bg-slate-100"
          >
            <ListChecks className="h-4 w-4" aria-hidden />
            Incidents
          </Link>
          <a
            href="https://github.com/PeterYousefi/AegisOps#readme"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 rounded-lg px-3 py-2 font-medium text-slate-500 hover:bg-slate-100"
          >
            <BookOpen className="h-4 w-4" aria-hidden />
            Docs
          </a>
        </nav>
        <div className="mt-auto px-5 py-4 text-xs text-slate-400">
          Synthetic data · simulated actions
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-6 py-3 backdrop-blur">
          <div className="flex items-center gap-2 sm:hidden">
            <ShieldCheck className="h-5 w-5 text-accent" aria-hidden />
            <span className="font-semibold">AegisOps</span>
          </div>
          <div className="hidden text-sm text-slate-500 sm:block">
            Human-Governed AI Incident Response
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-accent-soft text-xs font-semibold text-accent">
              OP
            </span>
            <span className="hidden sm:inline">On-call Operator</span>
          </div>
        </header>

        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
