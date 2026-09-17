"use client";

import { useState } from "react";
import type { EvidenceRecord } from "@/lib/types";
import { formatDateTime, humanize } from "@/lib/format";

const TYPE_STYLES: Record<string, string> = {
  alert: "bg-red-50 text-red-700 border-red-200",
  metric: "bg-blue-50 text-blue-700 border-blue-200",
  log: "bg-slate-50 text-slate-700 border-slate-200",
  deployment: "bg-purple-50 text-purple-700 border-purple-200",
  runbook: "bg-emerald-50 text-emerald-700 border-emerald-200",
  operator_note: "bg-amber-50 text-amber-700 border-amber-200",
};

/** A single, expandable evidence entry in the timeline. */
export function EvidenceItem({ evidence }: { evidence: EvidenceRecord }) {
  const [open, setOpen] = useState(false);
  const badge = TYPE_STYLES[evidence.evidence_type] ?? TYPE_STYLES.log;

  return (
    // Stable id so evidence citations can link/scroll here later.
    <li id={`evidence-${evidence.id}`} className="rounded-lg border border-gray-200 p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <span
            className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${badge}`}
          >
            {humanize(evidence.evidence_type)}
          </span>
          <p className="mt-1 text-sm text-gray-900">{evidence.summary}</p>
          <p className="mt-0.5 text-xs text-gray-500">
            {evidence.source ? `${evidence.source} · ` : ""}
            {formatDateTime(evidence.observed_at ?? evidence.created_at)}
          </p>
        </div>
        <button
          type="button"
          aria-expanded={open}
          className="shrink-0 text-xs text-blue-700 hover:underline"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? "Hide details" : "Show details"}
        </button>
      </div>
      {open && (
        <pre className="mt-2 overflow-x-auto rounded bg-gray-50 p-2 text-xs text-gray-800">
          {JSON.stringify(evidence.payload, null, 2)}
        </pre>
      )}
    </li>
  );
}
