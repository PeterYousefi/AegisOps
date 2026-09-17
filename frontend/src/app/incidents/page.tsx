"use client";

import { useEffect, useState } from "react";
import { getIncidents } from "@/lib/api";
import type { IncidentSummary } from "@/lib/types";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Spinner } from "@/components/ui/spinner";
import { IncidentCard } from "@/components/incidents/incident-card";
import { IncidentTable } from "@/components/incidents/incident-table";
import {
  IncidentFilters,
  type IncidentFilterValue,
} from "@/components/incidents/incident-filters";

type LoadState = "loading" | "error" | "ready";

/**
 * Incident list page. Fetches incidents from the backend, supports status and
 * severity filtering, and renders explicit loading, error, and empty states.
 */
export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [filters, setFilters] = useState<IncidentFilterValue>({});

  useEffect(() => {
    const controller = new AbortController();
    setState("loading");
    getIncidents(filters, controller.signal)
      .then((data) => {
        setIncidents(data);
        setState("ready");
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        setState("error");
        // Avoid surfacing raw error internals to the user.
        console.error("Failed to load incidents", err);
      });
    return () => controller.abort();
  }, [filters]);

  return (
    <main className="mx-auto max-w-5xl p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold">Incidents</h1>
        <p className="mt-1 text-sm text-gray-600">
          AegisOps incident dashboard
        </p>
      </header>

      <div className="mb-4">
        <IncidentFilters value={filters} onChange={setFilters} />
      </div>

      {state === "loading" && (
        <div className="py-12 text-center">
          <Spinner label="Loading incidents" />
        </div>
      )}

      {state === "error" && (
        <ErrorState message="Could not load incidents. Please try again." />
      )}

      {state === "ready" && incidents.length === 0 && (
        <EmptyState
          title="No incidents match these filters"
          description="Try clearing the filters to see all incidents."
        />
      )}

      {state === "ready" && incidents.length > 0 && (
        <>
          {/* Cards on small screens, table on larger screens. */}
          <div className="grid gap-3 sm:hidden">
            {incidents.map((incident) => (
              <IncidentCard key={incident.id} incident={incident} />
            ))}
          </div>
          <div className="hidden sm:block">
            <IncidentTable incidents={incidents} />
          </div>
        </>
      )}
    </main>
  );
}
