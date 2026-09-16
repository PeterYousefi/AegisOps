import { EmptyState } from "@/components/ui/empty-state";

/**
 * Incident list page — placeholder scaffold.
 *
 * The full incident list (data fetching, filters, card/table, loading/empty/
 * error states) is implemented in a later task (Milestone 3). For now this
 * establishes the route and layout shell.
 */
export default function IncidentsPage() {
  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-semibold">Incidents</h1>
      <p className="mt-1 text-sm text-gray-600">
        AegisOps incident dashboard
      </p>

      <div className="mt-8">
        <EmptyState
          title="No incidents to show yet"
          description="The incident list is wired up in a later task. This page confirms the route and layout are in place."
        />
      </div>
    </main>
  );
}
