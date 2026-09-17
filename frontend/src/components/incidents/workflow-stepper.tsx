import { Check } from "lucide-react";
import type { IncidentStatus } from "@/lib/types";

// The linear "happy path" the operator moves an incident through.
const STEPS: { key: IncidentStatus; label: string }[] = [
  { key: "detected", label: "Detected" },
  { key: "investigating", label: "Investigating" },
  { key: "awaiting_approval", label: "Awaiting approval" },
  { key: "mitigating", label: "Mitigating" },
  { key: "mitigated", label: "Mitigated" },
];

const ORDER: IncidentStatus[] = STEPS.map((s) => s.key);

/** Horizontal progress stepper showing where an incident is in its lifecycle. */
export function WorkflowStepper({ status }: { status: IncidentStatus }) {
  // "resolved" sits past "mitigated"; treat it as fully complete.
  const currentIndex =
    status === "resolved" ? STEPS.length - 1 : ORDER.indexOf(status);

  return (
    <ol className="flex flex-wrap items-center gap-y-2">
      {STEPS.map((step, i) => {
        const done = i < currentIndex;
        const active = i === currentIndex;
        return (
          <li key={step.key} className="flex items-center">
            <span
              className={[
                "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold",
                done
                  ? "bg-accent text-white"
                  : active
                    ? "bg-accent-soft text-accent ring-2 ring-accent"
                    : "bg-slate-100 text-slate-400",
              ].join(" ")}
            >
              {done ? <Check className="h-3.5 w-3.5" aria-hidden /> : i + 1}
            </span>
            <span
              className={[
                "ml-2 text-xs font-medium",
                active
                  ? "text-slate-900"
                  : done
                    ? "text-slate-600"
                    : "text-slate-400",
              ].join(" ")}
            >
              {step.label}
            </span>
            {i < STEPS.length - 1 && (
              <span
                className={`mx-2 h-px w-8 ${
                  i < currentIndex ? "bg-accent" : "bg-slate-200"
                }`}
                aria-hidden
              />
            )}
          </li>
        );
      })}
    </ol>
  );
}
