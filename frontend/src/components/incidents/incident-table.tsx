import Link from "next/link";
import type { IncidentSummary, Severity } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { SeverityBadge } from "./severity-badge";
import { StatusBadge } from "./status-badge";

const ACCENT: Record<Severity, string> = {
  sev1: "border-l-red-500",
  sev2: "border-l-orange-500",
  sev3: "border-l-amber-500",
  sev4: "border-l-transparent",
};

/** Table representation of incidents (used on wide screens). */
export function IncidentTable({ incidents }: { incidents: IncidentSummary[] }) {
  return (
    <div className="card overflow-hidden">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <th className="px-4 py-2.5 font-medium">Ref</th>
            <th className="px-4 py-2.5 font-medium">Incident</th>
            <th className="px-4 py-2.5 font-medium">Severity</th>
            <th className="px-4 py-2.5 font-medium">Status</th>
            <th className="px-4 py-2.5 font-medium">Service</th>
            <th className="px-4 py-2.5 font-medium">Owner</th>
            <th className="px-4 py-2.5 font-medium">Updated</th>
          </tr>
        </thead>
        <tbody>
          {incidents.map((incident) => (
            <tr
              key={incident.id}
              className={`border-b border-l-4 border-slate-100 ${ACCENT[incident.severity]} last:border-b-0 hover:bg-slate-50`}
            >
              <td className="px-4 py-3">
                <span className="font-mono text-xs text-slate-500">
                  {incident.reference}
                </span>
              </td>
              <td className="px-4 py-3">
                <Link
                  href={`/incidents/${incident.id}`}
                  className="font-medium text-slate-900 hover:text-accent"
                >
                  {incident.title}
                </Link>
                {incident.ai_summary ? (
                  <p className="mt-0.5 line-clamp-1 text-xs text-slate-500">
                    {incident.ai_summary}
                  </p>
                ) : null}
              </td>
              <td className="px-4 py-3">
                <SeverityBadge severity={incident.severity} />
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={incident.status} />
              </td>
              <td className="px-4 py-3 text-slate-700">
                {incident.affected_service}
              </td>
              <td className="px-4 py-3 text-slate-700">
                {incident.assigned_operator ?? "Unassigned"}
              </td>
              <td className="px-4 py-3 text-slate-500">
                {formatDateTime(incident.updated_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
