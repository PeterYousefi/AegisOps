import { AlertTriangle } from "lucide-react";

/**
 * Reusable error-state block. Shows a safe, human-readable message; never
 * renders raw error internals or stack traces to the user.
 */
export function ErrorState({
  title = "Something went wrong",
  message,
}: {
  title?: string;
  message?: string;
}) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4"
    >
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" aria-hidden />
      <div>
        <p className="text-sm font-medium text-red-800">{title}</p>
        {message ? <p className="mt-0.5 text-sm text-red-700">{message}</p> : null}
      </div>
    </div>
  );
}
