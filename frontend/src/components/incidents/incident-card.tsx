import Link from "next/link";
import type { IncidentSummary } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { SeverityBadge } from "./severity-badge";
import { StatusBadge } from "./status-badge";

/** Card representation of an incident (used on narrow screens). */
export function IncidentCard({ incident }: { incident: IncidentSummary }) {
  return (
    <Link
      href={`/incidents/${incident.id}`}
      className="block rounded-lg border border-gray-200 p-4 hover:border-gray-300 hover:shadow-sm"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-medium text-gray-900">{incident.title}</h3>
        <SeverityBadge severity={incident.severity} />
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-gray-600">
        <StatusBadge status={incident.status} />
        <span>{incident.affected_service}</span>
      </div>
      {incident.ai_summary ? (
        <p className="mt-2 line-clamp-2 text-sm text-gray-600">
          {incident.ai_summary}
        </p>
      ) : null}
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
        <span>Owner: {incident.assigned_operator ?? "Unassigned"}</span>
        <span>Created: {formatDateTime(incident.created_at)}</span>
        <span>Updated: {formatDateTime(incident.updated_at)}</span>
      </div>
    </Link>
  );
}
