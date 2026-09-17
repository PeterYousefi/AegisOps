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

/** Evidence types (mirrors backend EvidenceType enum values). */
export type EvidenceType =
  | "alert"
  | "metric"
  | "log"
  | "deployment"
  | "runbook"
  | "operator_note";

export const EVIDENCE_TYPES: EvidenceType[] = [
  "alert",
  "metric",
  "log",
  "deployment",
  "runbook",
  "operator_note",
];

/** A single evidence record (mirrors backend EvidenceOut). */
export interface EvidenceRecord {
  id: string;
  incident_id: string;
  evidence_type: EvidenceType;
  source: string | null;
  summary: string;
  payload: Record<string, unknown>;
  observed_at: string | null;
  created_at: string;
}

/** An audit event (mirrors backend AuditEventOut). */
export interface AuditEvent {
  id: string;
  incident_id: string | null;
  event_type: string;
  actor_type: string;
  actor_id: string;
  previous_state: string | null;
  new_state: string | null;
  metadata: Record<string, unknown>;
  correlation_id: string | null;
  created_at: string;
}

/** Full incident detail (mirrors backend IncidentDetail). */
export interface IncidentDetail extends IncidentSummary {
  evidence: EvidenceRecord[];
  audit_events: AuditEvent[];
}

/** AI incident assessment (mirrors backend AssessmentOut). */
export interface Assessment {
  id: string;
  incident_id: string;
  provider: string;
  executive_summary: string;
  severity: Severity;
  affected_services: string[];
  likely_root_cause: string;
  confidence_score: number;
  evidence_references: string[];
  runbook_references: string[];
  recommended_next_steps: string[];
  uncertainties: string[];
  safety_notes: string[];
  validation_status: "valid" | "invalid_fallback";
  created_at: string;
}
