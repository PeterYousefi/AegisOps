"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, generateReport, getReport } from "@/lib/api";
import type { Report } from "@/lib/types";
import { Spinner } from "@/components/ui/spinner";
import { ErrorState } from "@/components/ui/error-state";

function Block({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-800">{title}</h3>
      <p className="mt-0.5 text-sm text-gray-700">{text}</p>
    </div>
  );
}

function BulletBlock({ title, items }: { title: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-800">{title}</h3>
      <ul className="mt-0.5 list-disc pl-5 text-sm text-gray-700">
        {items.map((it, i) => (
          <li key={i}>{it}</li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Post-incident report section. Only generatable after mitigation; the button
 * is enabled based on incident status passed from the parent.
 */
export function ReportSection({
  incidentId,
  canGenerate,
}: {
  incidentId: string;
  canGenerate: boolean;
}) {
  const [report, setReport] = useState<Report | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setReport(await getReport(incidentId));
    } catch (err) {
      if (!(err instanceof ApiError && err.status === 404)) {
        // Non-404 errors are surfaced; a missing report is normal.
      }
    } finally {
      setLoading(false);
    }
  }, [incidentId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const generate = async () => {
    setBusy(true);
    setError(null);
    try {
      setReport(await generateReport(incidentId));
    } catch {
      setError("Could not generate the report. The incident must be mitigated first.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section aria-labelledby="report-heading">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 id="report-heading" className="text-lg font-semibold">
          Post-incident report
        </h2>
        {!report && (
          <button
            type="button"
            disabled={busy || !canGenerate}
            title={canGenerate ? undefined : "Available after mitigation"}
            onClick={generate}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {busy ? "Generating…" : "Generate report"}
          </button>
        )}
      </div>

      {loading && <Spinner label="Loading report" />}
      {error && <ErrorState message={error} />}

      {!loading && !report && (
        <p className="text-sm text-gray-600">
          {canGenerate
            ? "No report yet. Generate one to summarize the incident."
            : "A report can be generated after the incident is mitigated."}
        </p>
      )}

      {report && (
        <div className="space-y-3 rounded-lg border border-gray-200 p-4">
          <Block title="Timeline" text={report.timeline_summary} />
          <Block title="Customer impact" text={report.customer_impact_summary} />
          <Block title="Root cause" text={report.root_cause_summary} />
          <Block title="Remediation" text={report.remediation_summary} />
          <BulletBlock title="Follow-up actions" items={report.follow_up_actions} />
          <BulletBlock title="Lessons learned" items={report.lessons_learned} />
        </div>
      )}
    </section>
  );
}
