/**
 * Typed backend API surface.
 *
 * Re-exports the client primitives and exposes feature-specific typed calls.
 * For T1.3 only the health check exists; incident/evidence/AI/remediation
 * calls are added in later tasks.
 */

import { apiFetch } from "./client";
import type {
  Assessment,
  Execution,
  HealthResponse,
  IncidentDetail,
  IncidentStatus,
  IncidentSummary,
  Proposal,
  Report,
  Severity,
} from "@/lib/types";

export { apiFetch, ApiError, API_BASE_URL } from "./client";

/** GET /api/v1/health — backend liveness check. */
export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/api/v1/health", { signal });
}

export interface IncidentFilters {
  status?: IncidentStatus;
  severity?: Severity;
}

/** GET /api/v1/incidents — list incidents, optionally filtered. */
export function getIncidents(
  filters: IncidentFilters = {},
  signal?: AbortSignal,
): Promise<IncidentSummary[]> {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.severity) params.set("severity", filters.severity);
  const query = params.toString();
  const path = query ? `/api/v1/incidents?${query}` : "/api/v1/incidents";
  return apiFetch<IncidentSummary[]>(path, { signal });
}

/** GET /api/v1/incidents/{id} — full incident detail with nested relations. */
export function getIncident(
  id: string,
  signal?: AbortSignal,
): Promise<IncidentDetail> {
  return apiFetch<IncidentDetail>(
    `/api/v1/incidents/${encodeURIComponent(id)}`,
    { signal },
  );
}

/** POST /api/v1/incidents/{id}/assess — run AI assessment. */
export function assessIncident(
  id: string,
  signal?: AbortSignal,
): Promise<Assessment> {
  return apiFetch<Assessment>(
    `/api/v1/incidents/${encodeURIComponent(id)}/assess`,
    { method: "POST", signal },
  );
}

/** GET /api/v1/incidents/{id}/assessment — latest assessment (404 if none). */
export function getAssessment(
  id: string,
  signal?: AbortSignal,
): Promise<Assessment> {
  return apiFetch<Assessment>(
    `/api/v1/incidents/${encodeURIComponent(id)}/assessment`,
    { signal },
  );
}

/** GET /api/v1/incidents/{id}/proposals — list proposals (newest first). */
export function getProposals(
  id: string,
  signal?: AbortSignal,
): Promise<Proposal[]> {
  return apiFetch<Proposal[]>(
    `/api/v1/incidents/${encodeURIComponent(id)}/proposals`,
    { signal },
  );
}

/** POST /api/v1/incidents/{id}/proposals — generate a remediation proposal. */
export function createProposal(id: string): Promise<Proposal> {
  return apiFetch<Proposal>(
    `/api/v1/incidents/${encodeURIComponent(id)}/proposals`,
    { method: "POST" },
  );
}

/** POST /api/v1/proposals/{id}/approve */
export function approveProposal(
  proposalId: string,
  comment?: string,
): Promise<unknown> {
  return apiFetch(`/api/v1/proposals/${encodeURIComponent(proposalId)}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment: comment ?? null }),
  });
}

/** POST /api/v1/proposals/{id}/reject */
export function rejectProposal(
  proposalId: string,
  comment?: string,
): Promise<unknown> {
  return apiFetch(`/api/v1/proposals/${encodeURIComponent(proposalId)}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment: comment ?? null }),
  });
}

/** POST /api/v1/proposals/{id}/execute — run the simulated remediation. */
export function executeProposal(proposalId: string): Promise<Execution> {
  return apiFetch<Execution>(
    `/api/v1/proposals/${encodeURIComponent(proposalId)}/execute`,
    { method: "POST" },
  );
}

/** GET /api/v1/proposals/{id}/execution — latest execution (404 if none). */
export function getExecution(
  proposalId: string,
  signal?: AbortSignal,
): Promise<Execution> {
  return apiFetch<Execution>(
    `/api/v1/proposals/${encodeURIComponent(proposalId)}/execution`,
    { signal },
  );
}

/** POST /api/v1/incidents/{id}/report — generate the post-incident report. */
export function generateReport(id: string): Promise<Report> {
  return apiFetch<Report>(
    `/api/v1/incidents/${encodeURIComponent(id)}/report`,
    { method: "POST" },
  );
}

/** GET /api/v1/incidents/{id}/report — latest report (404 if none). */
export function getReport(id: string, signal?: AbortSignal): Promise<Report> {
  return apiFetch<Report>(
    `/api/v1/incidents/${encodeURIComponent(id)}/report`,
    { signal },
  );
}
