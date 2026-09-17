import type { Severity } from "@/lib/types";

const STYLES: Record<Severity, string> = {
  sev1: "bg-red-100 text-red-800 border-red-200",
  sev2: "bg-orange-100 text-orange-800 border-orange-200",
  sev3: "bg-amber-100 text-amber-800 border-amber-200",
  sev4: "bg-slate-100 text-slate-700 border-slate-200",
};

/** Colored badge for an incident severity. */
export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold uppercase ${STYLES[severity]}`}
    >
      {severity}
    </span>
  );
}
