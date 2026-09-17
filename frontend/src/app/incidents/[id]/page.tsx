"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ApiError, getIncident } from "@/lib/api";
import type { IncidentDetail } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { Spinner } from "@/components/ui/spinner";
import { ErrorState } from "@/components/ui/error-state";
import { EmptyState } from "@/components/ui/empty-state";
import { SeverityBadge } from "@/components/incidents/severity-badge";
import { StatusBadge } from "@/components/incidents/status-badge";
import { EvidenceTimeline } from "@/components/evidence/evidence-timeline";
import { AuditTimeline } from "@/components/audit/audit-timeline";
import { AssessmentSection } from "@/components/ai/assessment-section";

type LoadState = "loading" | "error" | "not_found" | "ready";

/** Placeholder for sections implemented in later milestones. */
function ComingSoon({ title }: { title: string }) {
  return (
    <section>
      <h2 className="mb-3 text-lg font-semibold">{title}</h2>
      <EmptyState
        title="Not available yet"
        description="This section is implemented in a later milestone."
      />
    </section>
  );
}

export default function IncidentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [state, setState] = useState<LoadState>("loading");

  const load = useCallback(
    (signal?: AbortSignal) => {
      getIncident(id, signal)
        .then((data) => {
          setIncident(data);
          setState("ready");
        })
        .catch((err: unknown) => {
          if (signal?.aborted) return;
          if (err instanceof ApiError && err.status === 404) {
            setState("not_found");
          } else {
            setState("error");
            console.error("Failed to load incident", err);
          }
        });
    },
    [id],
  );

  useEffect(() => {
    const controller = new AbortController();
    setState("loading");
    load(controller.signal);
    return () => controller.abort();
  }, [load]);

  return (
    <main className="mx-auto max-w-4xl p-6">
      <Link href="/incidents" className="text-sm text-blue-700 hover:underline">
        ← Back to incidents
      </Link>

      {state === "loading" && (
        <div className="py-12 text-center">
          <Spinner label="Loading incident" />
        </div>
      )}

      {state === "error" && (
        <div className="mt-6">
          <ErrorState message="Could not load this incident. Please try again." />
        </div>
      )}

      {state === "not_found" && (
        <div className="mt-6">
          <EmptyState
            title="Incident not found"
            description="This incident does not exist or may have been removed."
          />
        </div>
      )}

      {state === "ready" && incident && (
        <div className="mt-4 space-y-8">
          <header>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-semibold">{incident.title}</h1>
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={incident.status} />
            </div>
            <p className="mt-1 text-sm text-gray-600">
              Service: {incident.affected_service} · Owner:{" "}
              {incident.assigned_operator ?? "Unassigned"} · Updated:{" "}
              {formatDateTime(incident.updated_at)}
            </p>
          </header>

          <section>
            <h2 className="mb-2 text-lg font-semibold">Summary</h2>
            <p className="text-sm text-gray-700">
              {incident.ai_summary ?? "No summary available yet."}
            </p>
          </section>

          <EvidenceTimeline evidence={incident.evidence} />

          <AssessmentSection incidentId={incident.id} onAssessed={() => load()} />

          <ComingSoon title="Remediation proposal" />
          <ComingSoon title="Post-incident report" />
          <ComingSoon title="Salesforce sync" />

          <AuditTimeline events={incident.audit_events} />
        </div>
      )}
    </main>
  );
}
