import Link from "next/link";
import { ChevronRight } from "lucide-react";
import type { IncidentSummary, Severity } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { SeverityBadge } from "./severity-badge";
import { StatusBadge } from "./status-badge";

const ACCENT: Record<Severity, string> = {
  sev1: "border-l-red-500",
  sev2: "border-l-orange-500",
  sev3: "border-l-amber-500",
  sev4: "border-l-slate-300",
};

/** Card representation of an incident (used on narrow screens). */
export function IncidentCard({ incident }: { incident: IncidentSummary }) {
  return (
    <Link
      href={`/incidents/${incident.id}`}
      className={`card block border-l-4 p-4 hover:shadow-md ${ACCENT[incident.severity]}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="font-mono text-xs text-slate-400">
            {incident.reference}
          </span>
          <h3 className="font-semibold text-slate-900">{incident.title}</h3>
        </div>
        <SeverityBadge severity={incident.severity} />
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600">
        <StatusBadge status={incident.status} />
        <span className="text-slate-400">·</span>
        <span>{incident.affected_service}</span>
      </div>
      {incident.ai_summary ? (
        <p className="mt-2 line-clamp-2 text-sm text-slate-600">
          {incident.ai_summary}
        </p>
      ) : null}
      <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
        <span>
          {incident.assigned_operator ?? "Unassigned"} ·{" "}
          {formatDateTime(incident.updated_at)}
        </span>
        <ChevronRight className="h-4 w-4 text-slate-400" aria-hidden />
      </div>
    </Link>
  );
}
