"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ApiError, getIncident } from "@/lib/api";
import type { IncidentDetail } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { Spinner } from "@/components/ui/spinner";
import { ErrorState } from "@/components/ui/error-state";
import { EmptyState } from "@/components/ui/empty-state";
import { SeverityBadge } from "@/components/incidents/severity-badge";
import { StatusBadge } from "@/components/incidents/status-badge";
import { WorkflowStepper } from "@/components/incidents/workflow-stepper";
import { EvidenceTimeline } from "@/components/evidence/evidence-timeline";
import { AddEvidenceForm } from "@/components/evidence/add-evidence-form";
import { AuditTimeline } from "@/components/audit/audit-timeline";
import { AssessmentSection } from "@/components/ai/assessment-section";
import { RemediationSection } from "@/components/remediation/remediation-section";
import { ReportSection } from "@/components/report/report-section";
import { SalesforceSection } from "@/components/salesforce/salesforce-section";

type LoadState = "loading" | "error" | "not_found" | "ready";

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
    <div className="mx-auto max-w-4xl p-6">
      <Link
        href="/incidents"
        className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-accent"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Back to incidents
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
        <div className="mt-4 space-y-6">
          <header className="card p-5">
            <div className="font-mono text-xs text-slate-400">
              {incident.reference}
            </div>
            <div className="mt-1 flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-semibold tracking-tight">
                {incident.title}
              </h1>
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={incident.status} />
            </div>
            <p className="mt-1 text-sm text-slate-500">
              Service: {incident.affected_service} · Owner:{" "}
              {incident.assigned_operator ?? "Unassigned"} · Updated:{" "}
              {formatDateTime(incident.updated_at)}
            </p>
            <div className="mt-4 border-t border-slate-100 pt-4">
              <WorkflowStepper status={incident.status} />
            </div>
            {incident.ai_summary ? (
              <p className="mt-4 text-sm text-slate-700">{incident.ai_summary}</p>
            ) : null}
          </header>

          <div className="card p-5">
            <EvidenceTimeline evidence={incident.evidence} />
            <div className="mt-3 border-t border-slate-100 pt-3">
              <AddEvidenceForm incidentId={incident.id} onAdded={() => load()} />
            </div>
          </div>

          <div className="card p-5">
            <AssessmentSection
              incidentId={incident.id}
              evidence={incident.evidence}
              onAssessed={() => load()}
            />
          </div>

          <div className="card p-5">
            <RemediationSection incidentId={incident.id} onChanged={() => load()} />
          </div>

          <div className="card p-5">
            <ReportSection
              incidentId={incident.id}
              canGenerate={
                incident.status === "mitigated" || incident.status === "resolved"
              }
            />
          </div>

          <div className="card p-5">
            <SalesforceSection incidentId={incident.id} />
          </div>

          <div className="card p-5">
            <AuditTimeline events={incident.audit_events} />
          </div>
        </div>
      )}
    </div>
  );
}
