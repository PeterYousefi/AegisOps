"use client";

import { useEffect, useState } from "react";
import { ApiError, assessIncident, getAssessment } from "@/lib/api";
import type { Assessment, EvidenceRecord } from "@/lib/types";
import { humanize } from "@/lib/format";
import { Spinner } from "@/components/ui/spinner";
import { ErrorState } from "@/components/ui/error-state";
import { AssessmentPanel } from "./assessment-panel";

type State = "loading" | "none" | "ready" | "running" | "error";

/**
 * AI assessment section: loads the latest assessment on mount (if any) and lets
 * the operator run analysis on demand. On success it can notify the parent so
 * the incident (e.g. status) can be refreshed.
 */
export function AssessmentSection({
  incidentId,
  evidence = [],
  onAssessed,
}: {
  incidentId: string;
  evidence?: EvidenceRecord[];
  onAssessed?: () => void;
}) {
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [state, setState] = useState<State>("loading");

  // Map evidence id -> readable label ("Alert: 5xx ratio…") for citations.
  const evidenceLabels: Record<string, string> = {};
  for (const e of evidence) {
    const summary = e.summary.length > 40 ? `${e.summary.slice(0, 40)}…` : e.summary;
    evidenceLabels[e.id] = `${humanize(e.evidence_type)}: ${summary}`;
  }

  useEffect(() => {
    const controller = new AbortController();
    getAssessment(incidentId, controller.signal)
      .then((a) => {
        setAssessment(a);
        setState("ready");
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        if (err instanceof ApiError && err.status === 404) {
          setState("none");
        } else {
          setState("error");
        }
      });
    return () => controller.abort();
  }, [incidentId]);

  const run = async () => {
    setState("running");
    try {
      const a = await assessIncident(incidentId);
      setAssessment(a);
      setState("ready");
      onAssessed?.();
    } catch {
      setState("error");
    }
  };

  return (
    <section aria-labelledby="assessment-heading">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 id="assessment-heading" className="text-lg font-semibold">
          AI assessment
        </h2>
        <button
          type="button"
          onClick={run}
          disabled={state === "running"}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {state === "running"
            ? "Analyzing…"
            : assessment
              ? "Re-run analysis"
              : "Run AI analysis"}
        </button>
      </div>

      {state === "loading" && <Spinner label="Loading assessment" />}
      {state === "running" && <Spinner label="Running analysis" />}
      {state === "error" && (
        <ErrorState message="Could not run or load the assessment." />
      )}
      {(state === "none" || (state === "ready" && !assessment)) && (
        <p className="text-sm text-gray-600">
          No assessment yet. Run AI analysis to generate an evidence-grounded
          assessment.
        </p>
      )}
      {state === "ready" && assessment && (
        <AssessmentPanel assessment={assessment} evidenceLabels={evidenceLabels} />
      )}
    </section>
  );
}
