"use client";

/**
 * A clickable citation that scrolls to the referenced evidence item and
 * briefly highlights it. Traceability: every citation points to a real,
 * rendered evidence element (id="evidence-{id}").
 */
export function EvidenceCitation({ evidenceId }: { evidenceId: string }) {
  const onClick = () => {
    const el = document.getElementById(`evidence-${evidenceId}`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.add("ring-2", "ring-blue-400");
      window.setTimeout(
        () => el.classList.remove("ring-2", "ring-blue-400"),
        1500,
      );
    }
  };
  const short = evidenceId.length > 8 ? `${evidenceId.slice(0, 8)}…` : evidenceId;
  return (
    <button
      type="button"
      onClick={onClick}
      title={`Go to evidence ${evidenceId}`}
      className="inline-flex items-center rounded border border-blue-200 bg-blue-50 px-1.5 py-0.5 text-xs font-medium text-blue-700 hover:bg-blue-100"
    >
      evidence:{short}
    </button>
  );
}

/** A non-interactive runbook citation chip (runbooks are not on this page). */
export function RunbookCitation({ runbookId }: { runbookId: string }) {
  const short = runbookId.length > 8 ? `${runbookId.slice(0, 8)}…` : runbookId;
  return (
    <span
      title={`Runbook ${runbookId}`}
      className="inline-flex items-center rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-700"
    >
      runbook:{short}
    </span>
  );
}
