"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { addEvidence } from "@/lib/api";
import type { EvidenceType } from "@/lib/types";
import { EVIDENCE_TYPES } from "@/lib/types";
import { humanize } from "@/lib/format";

/**
 * Inline form to attach an evidence record to an incident. Calls onAdded after
 * a successful create so the parent can refresh.
 */
export function AddEvidenceForm({
  incidentId,
  onAdded,
}: {
  incidentId: string;
  onAdded: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<EvidenceType>("operator_note");
  const [summary, setSummary] = useState("");
  const [source, setSource] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await addEvidence(incidentId, {
        evidence_type: type,
        summary: summary.trim(),
        source: source.trim() || null,
      });
      setSummary("");
      setSource("");
      setOpen(false);
      onAdded();
    } catch {
      setError("Could not add evidence.");
    } finally {
      setBusy(false);
    }
  };

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
      >
        <Plus className="h-4 w-4" aria-hidden />
        Add evidence
      </button>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-2 rounded-lg border border-slate-200 p-3">
      <div className="grid gap-2 sm:grid-cols-2">
        <label className="text-sm">
          <span className="font-medium text-slate-700">Type</span>
          <select
            value={type}
            onChange={(e) => setType(e.target.value as EvidenceType)}
            className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          >
            {EVIDENCE_TYPES.map((t) => (
              <option key={t} value={t}>
                {humanize(t)}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="font-medium text-slate-700">Source (optional)</span>
          <input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
            placeholder="e.g. monitoring"
          />
        </label>
      </div>
      <label className="block text-sm">
        <span className="font-medium text-slate-700">Summary</span>
        <input
          required
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          placeholder="What was observed?"
        />
      </label>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-100"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={busy}
          className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60"
        >
          {busy ? "Adding…" : "Add"}
        </button>
      </div>
    </form>
  );
}
