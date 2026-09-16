/**
 * Typed backend API surface.
 *
 * Re-exports the client primitives and exposes feature-specific typed calls.
 * For T1.3 only the health check exists; incident/evidence/AI/remediation
 * calls are added in later tasks.
 */

import { apiFetch } from "./client";
import type { HealthResponse } from "@/lib/types";

export { apiFetch, ApiError, API_BASE_URL } from "./client";

/** GET /api/v1/health — backend liveness check. */
export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/api/v1/health", { signal });
}
