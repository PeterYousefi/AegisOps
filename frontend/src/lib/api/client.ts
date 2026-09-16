/**
 * Typed API client for the AegisOps backend.
 *
 * All frontend calls to the backend go through this single wrapper so that
 * base URL resolution, JSON handling, and error normalization live in one
 * place. Feature-specific typed calls live alongside this module.
 */

/** Base URL of the backend API, from the environment (local default). */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * Normalized API error. Carries a safe, human-readable message and the HTTP
 * status when available. Raw response bodies are not surfaced to the UI.
 */
export class ApiError extends Error {
  readonly status: number | null;

  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Perform a typed JSON request against the backend API.
 *
 * @param path API path beginning with "/", e.g. "/api/v1/health".
 * @param init Optional fetch init (method, headers, body, signal).
 * @returns Parsed JSON typed as T.
 * @throws ApiError on network failure or a non-2xx response.
 */
export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch {
    // Network-level failure (server down, DNS, CORS at transport level).
    throw new ApiError("Unable to reach the AegisOps backend.");
  }

  if (!response.ok) {
    throw new ApiError(
      `Request to ${path} failed (HTTP ${response.status}).`,
      response.status,
    );
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError(`Received an invalid response from ${path}.`);
  }
}

export { API_BASE_URL };
