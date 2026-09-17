/**
 * Shared TypeScript types mirroring backend Pydantic schemas.
 *
 * Kept in sync with the FastAPI backend. As new endpoints are added in later
 * tasks (evidence detail, AI assessment, remediation, etc.), their response
 * types are added here.
 */

/** Response shape of GET /api/v1/health. Mirrors backend HealthResponse. */
export interface HealthResponse {
  status: string;
  service: string;
  environment: string;
}

/** Incident severity levels (mirrors backend Severity enum values). */
export type Severity = "sev1" | "sev2" | "sev3" | "sev4";

/** Incident lifecycle statuses (mirrors backend IncidentStatus enum values). */
export type IncidentStatus =
  | "detected"
  | "investigating"
  | "awaiting_approval"
  | "mitigating"
  | "mitigated"
  | "resolved";

/** List-view incident (mirrors backend IncidentSummary). */
export interface IncidentSummary {
  id: string;
  title: string;
  severity: Severity;
  status: IncidentStatus;
  affected_service: string;
  assigned_operator: string | null;
  ai_summary: string | null;
  created_at: string;
  updated_at: string;
}

export const SEVERITIES: Severity[] = ["sev1", "sev2", "sev3", "sev4"];

export const INCIDENT_STATUSES: IncidentStatus[] = [
  "detected",
  "investigating",
  "awaiting_approval",
  "mitigating",
  "mitigated",
  "resolved",
];
