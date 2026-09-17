"use client";

import { useMemo, useState } from "react";
import type { EvidenceRecord, EvidenceType } from "@/lib/types";
import { EVIDENCE_TYPES } from "@/lib/types";
import { humanize } from "@/lib/format";
import { EmptyState } from "@/components/ui/empty-state";
import { EvidenceItem } from "./evidence-item";

/**
 * Evidence timeline with a client-side type filter. Evidence is already loaded
 * with the incident detail, so filtering happens in-memory.
 */
export function EvidenceTimeline({
  evidence,
}: {
  evidence: EvidenceRecord[];
}) {
  const [type, setType] = useState<EvidenceType | "">("");

  // Only offer filter options for types that are actually present.
  const availableTypes = useMemo(
    () => EVIDENCE_TYPES.filter((t) => evidence.some((e) => e.evidence_type === t)),
    [evidence],
  );

  const filtered = useMemo(
    () => (type ? evidence.filter((e) => e.evidence_type === type) : evidence),
    [evidence, type],
  );

  return (
    <section aria-labelledby="evidence-heading">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <h2 id="evidence-heading" className="text-lg font-semibold">
          Evidence
        </h2>
        <label className="flex items-center gap-2 text-sm">
          <span className="text-gray-700">Type</span>
          <select
            aria-label="Filter evidence by type"
            className="rounded-md border border-gray-300 px-2 py-1 text-sm"
            value={type}
            onChange={(e) => setType((e.target.value || "") as EvidenceType | "")}
          >
            <option value="">All types</option>
            {availableTypes.map((t) => (
              <option key={t} value={t}>
                {humanize(t)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No evidence for this filter" />
      ) : (
        <ul className="space-y-2">
          {filtered.map((e) => (
            <EvidenceItem key={e.id} evidence={e} />
          ))}
        </ul>
      )}
    </section>
  );
}
