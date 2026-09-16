/**
 * Shared TypeScript types mirroring backend Pydantic schemas.
 *
 * Kept in sync with the FastAPI backend. As new endpoints are added in later
 * tasks (incidents, evidence, AI assessment, remediation, etc.), their
 * response types are added here.
 */

/** Response shape of GET /api/v1/health. Mirrors backend HealthResponse. */
export interface HealthResponse {
  status: string;
  service: string;
  environment: string;
}
