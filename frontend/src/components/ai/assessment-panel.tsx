"use client";

import type { Assessment } from "@/lib/types";
import { ConfidenceMeter } from "./confidence-meter";
import { EvidenceCitation, RunbookCitation } from "./citation-chip";

function List({ title, items }: { title: string; items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-800">{title}</h3>
      <ul className="mt-1 list-disc pl-5 text-sm text-gray-700">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

/** Renders an AI assessment with clickable evidence citations. */
export function AssessmentPanel({
  assessment,
  evidenceLabels = {},
}: {
  assessment: Assessment;
  evidenceLabels?: Record<string, string>;
}) {
  const isFallback = assessment.validation_status === "invalid_fallback";
  return (
    <div className="space-y-4 rounded-lg border border-gray-200 p-4">
      {isFallback && (
        <div
          role="alert"
          className="rounded-md border border-amber-200 bg-amber-50 p-2 text-sm text-amber-800"
        >
          The automated assessment failed validation and a safe fallback is
          shown. No remediation should be based on it.
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-2">
        <ConfidenceMeter score={assessment.confidence_score} />
        <span className="text-xs text-gray-500">
          Provider: {assessment.provider} · {assessment.validation_status}
        </span>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-800">
          Executive summary
        </h3>
        <p className="mt-1 text-sm text-gray-700">
          {assessment.executive_summary}
        </p>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-800">
          Likely root cause
        </h3>
        <p className="mt-1 text-sm text-gray-700">
          {assessment.likely_root_cause}
        </p>
      </div>

      <List title="Recommended next steps" items={assessment.recommended_next_steps} />
      <List title="Uncertainties" items={assessment.uncertainties} />
      <List title="Safety notes" items={assessment.safety_notes} />

      {(assessment.evidence_references.length > 0 ||
        assessment.runbook_references.length > 0) && (
        <div>
          <h3 className="text-sm font-semibold text-gray-800">Citations</h3>
          <div className="mt-1 flex flex-wrap gap-1.5">
            {assessment.evidence_references.map((id) => (
              <EvidenceCitation key={id} evidenceId={id} label={evidenceLabels[id]} />
            ))}
            {assessment.runbook_references.map((id) => (
              <RunbookCitation key={id} runbookId={id} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
