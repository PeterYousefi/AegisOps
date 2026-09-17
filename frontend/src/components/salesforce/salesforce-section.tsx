"use client";

import { useCallback, useEffect, useState } from "react";
import { getIntegrationSyncs, syncSalesforce } from "@/lib/api";
import type { IntegrationSync } from "@/lib/types";
import { Spinner } from "@/components/ui/spinner";
import { ErrorState } from "@/components/ui/error-state";
import { formatDateTime } from "@/lib/format";

interface Ref {
  id?: string;
  url?: string;
}

function refEntries(refs: Record<string, unknown>): [string, Ref][] {
  return Object.entries(refs).filter(
    ([, v]) => typeof v === "object" && v !== null,
  ) as [string, Ref][];
}

/**
 * Fake Salesforce customer-impact sync. Manual only; shows returned synthetic
 * external IDs/URLs and the sync history. No real records or communications.
 */
export function SalesforceSection({ incidentId }: { incidentId: string }) {
  const [syncs, setSyncs] = useState<IntegrationSync[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setSyncs(await getIntegrationSyncs(incidentId));
    } finally {
      setLoading(false);
    }
  }, [incidentId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const run = async () => {
    setBusy(true);
    setError(null);
    try {
      await syncSalesforce(incidentId);
      await refresh();
    } catch {
      setError("Sync failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section aria-labelledby="salesforce-heading">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 id="salesforce-heading" className="text-lg font-semibold">
          Salesforce sync <span className="text-xs text-gray-500">(fake)</span>
        </h2>
        <button
          type="button"
          disabled={busy}
          onClick={run}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-60"
        >
          {busy ? "Syncing…" : "Sync customer impact"}
        </button>
      </div>

      <p className="mb-2 text-xs text-gray-500">
        Synthetic sync only — no real Salesforce records or communications.
      </p>

      {loading && <Spinner label="Loading sync history" />}
      {error && <ErrorState message={error} />}

      {!loading && syncs.length === 0 && (
        <p className="text-sm text-gray-600">No sync attempts yet.</p>
      )}

      {syncs.length > 0 && (
        <ul className="space-y-2">
          {syncs.map((s) => (
            <li key={s.id} className="rounded-lg border border-gray-200 p-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-medium">{s.status}</span>
                <span className="text-xs text-gray-400">
                  {formatDateTime(s.created_at)}
                </span>
              </div>
              {s.failure_reason && (
                <p className="mt-1 text-red-700">{s.failure_reason}</p>
              )}
              <ul className="mt-1 space-y-0.5">
                {refEntries(s.external_refs).map(([key, ref]) => (
                  <li key={key} className="text-gray-700">
                    <span className="font-medium">{key}:</span>{" "}
                    {ref.url ? (
                      <span className="text-blue-700">{ref.url}</span>
                    ) : (
                      ref.id
                    )}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
