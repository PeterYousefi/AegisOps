/**
 * Typed backend API surface.
 *
 * Re-exports the client primitives and exposes feature-specific typed calls.
 * For T1.3 only the health check exists; incident/evidence/AI/remediation
 * calls are added in later tasks.
 */

import { apiFetch } from "./client";
import type {
  HealthResponse,
  IncidentDetail,
  IncidentStatus,
  IncidentSummary,
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
