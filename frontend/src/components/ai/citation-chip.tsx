"use client";

/**
 * A clickable citation that scrolls to the referenced evidence item and
 * briefly highlights it. Traceability: every citation points to a real,
 * rendered evidence element (id="evidence-{id}").
 */
export function EvidenceCitation({
  evidenceId,
  label,
}: {
  evidenceId: string;
  label?: string;
}) {
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
  const text = label ?? `evidence ${evidenceId.slice(0, 8)}…`;
  return (
    <button
      type="button"
      onClick={onClick}
      title={`Go to evidence ${evidenceId}`}
      className="inline-flex max-w-full items-center gap-1 truncate rounded border border-blue-200 bg-blue-50 px-1.5 py-0.5 text-xs font-medium text-blue-700 hover:bg-blue-100"
    >
      <span aria-hidden>🔗</span>
      <span className="truncate">{text}</span>
    </button>
  );
}

/** A non-interactive runbook citation chip (runbooks are not on this page). */
export function RunbookCitation({
  runbookId,
  label,
}: {
  runbookId: string;
  label?: string;
}) {
  const text = label ?? `runbook ${runbookId.slice(0, 8)}…`;
  return (
    <span
      title={`Runbook ${runbookId}`}
      className="inline-flex max-w-full items-center gap-1 truncate rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-xs font-medium text-emerald-700"
    >
      <span aria-hidden>📘</span>
      <span className="truncate">{text}</span>
    </span>
  );
}
