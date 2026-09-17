"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertOctagon, Clock3, CheckCircle2, Activity } from "lucide-react";
import { getIncidents } from "@/lib/api";
import type { IncidentSummary } from "@/lib/types";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Spinner } from "@/components/ui/spinner";
import { IncidentCard } from "@/components/incidents/incident-card";
import { IncidentTable } from "@/components/incidents/incident-table";
import { StatCard } from "@/components/incidents/stat-card";
import { NewIncidentDialog } from "@/components/incidents/new-incident-dialog";
import {
  IncidentFilters,
  type IncidentFilterValue,
} from "@/components/incidents/incident-filters";

type LoadState = "loading" | "error" | "ready";

/**
 * Incident list page. Loads all incidents (for the summary strip) and applies
 * status/severity filtering client-side for the list. Explicit loading, error,
 * and empty states.
 */
export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [filters, setFilters] = useState<IncidentFilterValue>({});

  const load = (signal?: AbortSignal) => {
    setState("loading");
    getIncidents({}, signal)
      .then((data) => {
        setIncidents(data);
        setState("ready");
      })
      .catch((err: unknown) => {
        if (signal?.aborted) return;
        setState("error");
        console.error("Failed to load incidents", err);
      });
  };

  useEffect(() => {
    const controller = new AbortController();
    load(controller.signal);
    return () => controller.abort();
  }, []);

  const stats = useMemo(() => {
    return {
      total: incidents.length,
      critical: incidents.filter((i) => i.severity === "sev1").length,
      awaiting: incidents.filter((i) => i.status === "awaiting_approval").length,
      mitigated: incidents.filter(
        (i) => i.status === "mitigated" || i.status === "resolved",
      ).length,
    };
  }, [incidents]);

  const filtered = useMemo(
    () =>
      incidents.filter(
        (i) =>
          (!filters.status || i.status === filters.status) &&
          (!filters.severity || i.severity === filters.severity),
      ),
    [incidents, filters],
  );

  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Incidents</h1>
          <p className="mt-1 text-sm text-slate-500">
            Review, analyze, and remediate cloud operations incidents.
          </p>
        </div>
        <NewIncidentDialog onCreated={() => load()} />
      </header>

      {state === "ready" && (
        <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
          <StatCard label="Total" value={stats.total} icon={Activity} />
          <StatCard
            label="Critical (SEV1)"
            value={stats.critical}
            icon={AlertOctagon}
            tone="critical"
          />
          <StatCard
            label="Awaiting approval"
            value={stats.awaiting}
            icon={Clock3}
            tone="warning"
          />
          <StatCard
            label="Mitigated"
            value={stats.mitigated}
            icon={CheckCircle2}
            tone="success"
          />
        </div>
      )}

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

      {state === "ready" && filtered.length === 0 && (
        <EmptyState
          title="No incidents match these filters"
          description="Try clearing the filters to see all incidents."
        />
      )}

      {state === "ready" && filtered.length > 0 && (
        <>
          <div className="grid gap-3 sm:hidden">
            {filtered.map((incident) => (
              <IncidentCard key={incident.id} incident={incident} />
            ))}
          </div>
          <div className="hidden sm:block">
            <IncidentTable incidents={filtered} />
          </div>
        </>
      )}
    </div>
  );
}
