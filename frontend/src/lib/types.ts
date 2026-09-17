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
  reference: string;
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

/** Remediation proposal (mirrors backend ProposalOut). */
export interface Proposal {
  id: string;
  incident_id: string;
  assessment_id: string | null;
  action_type: string;
  action_description: string;
  justification: string;
  risk_level: string;
  blast_radius: string;
  prerequisites: string[];
  rollback_plan: string;
  expected_outcome: string;
  required_approval: boolean;
  evidence_references: string[];
  runbook_references: string[];
  status: string;
  created_at: string;
}

/** Simulated remediation execution (mirrors backend ExecutionOut). */
export interface Execution {
  id: string;
  proposal_id: string;
  action_type: string;
  status: "started" | "succeeded" | "failed";
  result: Record<string, unknown> | null;
  failure_reason: string | null;
  started_at: string;
  completed_at: string | null;
}

/** Integration sync record (mirrors backend IntegrationSyncOut). */
export interface IntegrationSync {
  id: string;
  incident_id: string;
  integration: string;
  sync_type: string;
  status: "requested" | "completed" | "failed";
  external_refs: Record<string, unknown>;
  failure_reason: string | null;
  created_at: string;
}

/** Post-incident report (mirrors backend ReportOut). */
export interface Report {
  id: string;
  incident_id: string;
  provider: string;
  timeline_summary: string;
  customer_impact_summary: string;
  root_cause_summary: string;
  remediation_summary: string;
  follow_up_actions: string[];
  lessons_learned: string[];
  created_at: string;
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
