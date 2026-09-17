"use client";

import { useCallback, useEffect, useState } from "react";
import {
  approveProposal,
  createProposal,
  executeProposal,
  getExecution,
  getProposals,
  rejectProposal,
} from "@/lib/api";
import type { Execution, Proposal } from "@/lib/types";
import { Spinner } from "@/components/ui/spinner";
import { ErrorState } from "@/components/ui/error-state";
import { ProposalCard } from "./proposal-card";

/**
 * Remediation section: generate a proposal, approve/reject it (with optional
 * comment), and run the simulated remediation. Every mutating action refreshes
 * the incident via onChanged so status/audit stay in sync.
 */
export function RemediationSection({
  incidentId,
  onChanged,
}: {
  incidentId: string;
  onChanged?: () => void;
}) {
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [execution, setExecution] = useState<Execution | null>(null);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const proposals = await getProposals(incidentId);
      const latest = proposals[0] ?? null;
      setProposal(latest);
      if (latest) {
        try {
          setExecution(await getExecution(latest.id));
        } catch {
          setExecution(null);
        }
      }
    } finally {
      setLoading(false);
    }
  }, [incidentId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const wrap = async (fn: () => Promise<unknown>) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      await refresh();
      onChanged?.();
    } catch {
      setError("Action failed. Check that the incident is in the right state.");
    } finally {
      setBusy(false);
    }
  };

  const isPending = proposal?.status === "pending";
  const isApproved = proposal?.status === "approved";
  const failed = execution?.status === "failed";

  return (
    <section aria-labelledby="remediation-heading">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 id="remediation-heading" className="text-lg font-semibold">
          Remediation proposal
        </h2>
        {!proposal && (
          <button
            type="button"
            disabled={busy}
            onClick={() => wrap(() => createProposal(incidentId))}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            Generate proposal
          </button>
        )}
      </div>

      {loading && <Spinner label="Loading remediation" />}
      {error && <ErrorState message={error} />}

      {!loading && !proposal && (
        <p className="text-sm text-gray-600">
          No proposal yet. Generate one after running the AI assessment.
        </p>
      )}

      {proposal && (
        <div className="space-y-4">
          <ProposalCard proposal={proposal} />

          {isPending && (
            <div className="space-y-2 rounded-lg border border-gray-200 p-3">
              <label className="block text-sm font-medium text-gray-700">
                Approval comment (optional)
                <textarea
                  className="mt-1 w-full rounded-md border border-gray-300 p-2 text-sm"
                  rows={2}
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                />
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => wrap(() => approveProposal(proposal.id, comment))}
                  className="rounded-md bg-green-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-60"
                >
                  Approve
                </button>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => wrap(() => rejectProposal(proposal.id, comment))}
                  className="rounded-md border border-red-300 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-60"
                >
                  Reject
                </button>
              </div>
            </div>
          )}

          {isApproved && !execution && (
            <button
              type="button"
              disabled={busy}
              onClick={() => wrap(() => executeProposal(proposal.id))}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
            >
              Run simulated remediation
            </button>
          )}

          {execution && (
            <div
              className={`rounded-lg border p-3 text-sm ${
                failed
                  ? "border-red-200 bg-red-50 text-red-800"
                  : "border-green-200 bg-green-50 text-green-800"
              }`}
              role={failed ? "alert" : undefined}
            >
              <p className="font-medium">
                Simulated remediation {execution.status}
              </p>
              {failed ? (
                <p className="mt-1">
                  {execution.failure_reason} Mitigation failed — further
                  investigation is required.
                </p>
              ) : (
                <p className="mt-1">The incident has been mitigated (simulated).</p>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
