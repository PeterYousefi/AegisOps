"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";
import { createIncident } from "@/lib/api";
import type { Severity } from "@/lib/types";
import { SEVERITIES } from "@/lib/types";

/**
 * "New incident" button that opens an inline dialog to create an incident.
 * Calls onCreated after a successful create so the list can refresh.
 */
export function NewIncidentDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [service, setService] = useState("");
  const [severity, setSeverity] = useState<Severity>("sev3");
  const [operator, setOperator] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reset = () => {
    setTitle("");
    setService("");
    setSeverity("sev3");
    setOperator("");
    setError(null);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await createIncident({
        title: title.trim(),
        severity,
        affected_service: service.trim(),
        assigned_operator: operator.trim() || null,
      });
      setOpen(false);
      reset();
      onCreated();
    } catch {
      setError("Could not create the incident. Please check the fields.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent-hover"
      >
        <Plus className="h-4 w-4" aria-hidden />
        New incident
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="new-incident-title"
            className="card w-full max-w-md p-5"
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 id="new-incident-title" className="text-lg font-semibold">
                New incident
              </h2>
              <button
                type="button"
                aria-label="Close"
                onClick={() => setOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" aria-hidden />
              </button>
            </div>

            <form onSubmit={submit} className="space-y-3">
              <label className="block text-sm">
                <span className="font-medium text-slate-700">Title</span>
                <input
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                  placeholder="e.g. Payments API elevated errors"
                />
              </label>

              <label className="block text-sm">
                <span className="font-medium text-slate-700">Affected service</span>
                <input
                  required
                  value={service}
                  onChange={(e) => setService(e.target.value)}
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                  placeholder="e.g. payments-api"
                />
              </label>

              <div className="grid grid-cols-2 gap-3">
                <label className="block text-sm">
                  <span className="font-medium text-slate-700">Severity</span>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value as Severity)}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                  >
                    {SEVERITIES.map((s) => (
                      <option key={s} value={s}>
                        {s.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block text-sm">
                  <span className="font-medium text-slate-700">Owner (optional)</span>
                  <input
                    value={operator}
                    onChange={(e) => setOperator(e.target.value)}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                    placeholder="you@example.com"
                  />
                </label>
              </div>

              {error && <p className="text-sm text-red-600">{error}</p>}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={busy}
                  className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60"
                >
                  {busy ? "Creating…" : "Create incident"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
