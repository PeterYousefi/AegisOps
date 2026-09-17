"use client";

import type { IncidentStatus, Severity } from "@/lib/types";
import { INCIDENT_STATUSES, SEVERITIES } from "@/lib/types";
import { humanize } from "@/lib/format";

export interface IncidentFilterValue {
  status?: IncidentStatus;
  severity?: Severity;
}

/** Status + severity filter controls for the incident list. */
export function IncidentFilters({
  value,
  onChange,
}: {
  value: IncidentFilterValue;
  onChange: (next: IncidentFilterValue) => void;
}) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <label className="flex flex-col text-sm">
        <span className="mb-1 font-medium text-gray-700">Status</span>
        <select
          aria-label="Filter by status"
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm"
          value={value.status ?? ""}
          onChange={(e) =>
            onChange({
              ...value,
              status: (e.target.value || undefined) as IncidentStatus | undefined,
            })
          }
        >
          <option value="">All statuses</option>
          {INCIDENT_STATUSES.map((s) => (
            <option key={s} value={s}>
              {humanize(s)}
            </option>
          ))}
        </select>
      </label>

      <label className="flex flex-col text-sm">
        <span className="mb-1 font-medium text-gray-700">Severity</span>
        <select
          aria-label="Filter by severity"
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm"
          value={value.severity ?? ""}
          onChange={(e) =>
            onChange({
              ...value,
              severity: (e.target.value || undefined) as Severity | undefined,
            })
          }
        >
          <option value="">All severities</option>
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>
              {s.toUpperCase()}
            </option>
          ))}
        </select>
      </label>

      {(value.status || value.severity) && (
        <button
          type="button"
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
          onClick={() => onChange({})}
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
