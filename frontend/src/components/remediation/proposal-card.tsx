import type { Proposal } from "@/lib/types";
import { humanize } from "@/lib/format";
import { EvidenceCitation, RunbookCitation } from "@/components/ai/citation-chip";

const RISK_STYLES: Record<string, string> = {
  low: "bg-green-100 text-green-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-800",
};

const RISK_LEVEL: Record<string, number> = { low: 1, medium: 2, high: 3 };
const RISK_FILL: Record<string, string> = {
  low: "bg-green-500",
  medium: "bg-amber-500",
  high: "bg-red-500",
};

function RiskGauge({ level }: { level: string }) {
  const active = RISK_LEVEL[level] ?? 0;
  return (
    <div className="flex items-center gap-1" aria-label={`Risk: ${level}`}>
      {[1, 2, 3].map((seg) => (
        <span
          key={seg}
          className={`h-1.5 w-5 rounded-full ${
            seg <= active ? RISK_FILL[level] : "bg-slate-200"
          }`}
        />
      ))}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-0.5 text-sm text-slate-800">{value}</dd>
    </div>
  );
}

/** Renders a remediation proposal with all decision-relevant fields. */
export function ProposalCard({
  proposal,
  evidenceLabels = {},
}: {
  proposal: Proposal;
  evidenceLabels?: Record<string, string>;
}) {
  return (
    <div className="space-y-3 rounded-xl border border-slate-200 bg-slate-50/50 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-semibold text-slate-900">
          {humanize(proposal.action_type)}
        </span>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${
            RISK_STYLES[proposal.risk_level] ?? "bg-gray-100 text-gray-700"
          }`}
        >
          {proposal.risk_level} risk
        </span>
        <RiskGauge level={proposal.risk_level} />
        <span className="ml-auto rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-700">
          {humanize(proposal.status)}
        </span>
      </div>

      <dl className="grid gap-3 sm:grid-cols-2">
        <Field label="Action" value={proposal.action_description} />
        <Field label="Justification" value={proposal.justification} />
        <Field label="Blast radius" value={proposal.blast_radius} />
        <Field label="Expected outcome" value={proposal.expected_outcome} />
        <Field label="Rollback plan" value={proposal.rollback_plan} />
        <div>
          <dt className="text-xs font-semibold uppercase text-gray-500">
            Prerequisites
          </dt>
          <dd className="mt-0.5 text-sm text-gray-800">
            <ul className="list-disc pl-5">
              {proposal.prerequisites.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </dd>
        </div>
      </dl>

      <div className="flex flex-wrap items-center gap-1.5">
        <span className="text-xs font-semibold uppercase text-gray-500">
          Requires approval:
        </span>
        <span className="text-sm text-gray-800">
          {proposal.required_approval ? "Yes" : "No"}
        </span>
      </div>

      {(proposal.evidence_references.length > 0 ||
        proposal.runbook_references.length > 0) && (
        <div className="flex flex-wrap gap-1.5">
          {proposal.evidence_references.map((id) => (
            <EvidenceCitation key={id} evidenceId={id} label={evidenceLabels[id]} />
          ))}
          {proposal.runbook_references.map((id) => (
            <RunbookCitation key={id} runbookId={id} />
          ))}
        </div>
      )}
    </div>
  );
}
