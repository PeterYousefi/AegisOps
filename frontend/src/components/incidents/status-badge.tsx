import type { IncidentStatus } from "@/lib/types";
import { humanize } from "@/lib/format";

const STYLES: Record<IncidentStatus, string> = {
  detected: "bg-slate-100 text-slate-700 border-slate-200",
  investigating: "bg-blue-100 text-blue-800 border-blue-200",
  awaiting_approval: "bg-purple-100 text-purple-800 border-purple-200",
  mitigating: "bg-amber-100 text-amber-800 border-amber-200",
  mitigated: "bg-green-100 text-green-800 border-green-200",
  resolved: "bg-gray-100 text-gray-700 border-gray-200",
};

/** Colored badge for an incident status. */
export function StatusBadge({ status }: { status: IncidentStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${STYLES[status]}`}
    >
      {humanize(status)}
    </span>
  );
}
