/**
 * Minimal accessible loading spinner.
 */
export function Spinner({ label = "Loading" }: { label?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="inline-flex items-center gap-2 text-sm text-gray-600"
    >
      <span
        aria-hidden="true"
        className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-700"
      />
      <span>{label}</span>
    </div>
  );
}
