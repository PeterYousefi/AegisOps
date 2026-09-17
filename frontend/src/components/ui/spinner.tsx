import { Loader2 } from "lucide-react";

/** Minimal accessible loading spinner. */
export function Spinner({ label = "Loading" }: { label?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="inline-flex items-center gap-2 text-sm text-slate-500"
    >
      <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
      <span>{label}</span>
    </div>
  );
}
