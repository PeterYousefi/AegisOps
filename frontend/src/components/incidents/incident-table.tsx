import Link from "next/link";
import type { IncidentSummary } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { SeverityBadge } from "./severity-badge";
import { StatusBadge } from "./status-badge";

/** Table representation of incidents (used on wide screens). */
export function IncidentTable({ incidents }: { incidents: IncidentSummary[] }) {
  return (
    <table className="w-full border-collapse text-left text-sm">
      <thead>
        <tr className="border-b border-gray-200 text-xs uppercase text-gray-500">
          <th className="py-2 pr-4 font-medium">Title</th>
          <th className="py-2 pr-4 font-medium">Severity</th>
          <th className="py-2 pr-4 font-medium">Status</th>
          <th className="py-2 pr-4 font-medium">Service</th>
          <th className="py-2 pr-4 font-medium">Owner</th>
          <th className="py-2 pr-4 font-medium">Updated</th>
        </tr>
      </thead>
      <tbody>
        {incidents.map((incident) => (
          <tr
            key={incident.id}
            className="border-b border-gray-100 hover:bg-gray-50"
          >
            <td className="py-2 pr-4">
              <Link
                href={`/incidents/${incident.id}`}
                className="font-medium text-blue-700 hover:underline"
              >
                {incident.title}
              </Link>
              {incident.ai_summary ? (
                <p className="mt-0.5 line-clamp-1 text-xs text-gray-500">
                  {incident.ai_summary}
                </p>
              ) : null}
            </td>
            <td className="py-2 pr-4">
              <SeverityBadge severity={incident.severity} />
            </td>
            <td className="py-2 pr-4">
              <StatusBadge status={incident.status} />
            </td>
            <td className="py-2 pr-4 text-gray-700">
              {incident.affected_service}
            </td>
            <td className="py-2 pr-4 text-gray-700">
              {incident.assigned_operator ?? "Unassigned"}
            </td>
            <td className="py-2 pr-4 text-gray-500">
              {formatDateTime(incident.updated_at)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
