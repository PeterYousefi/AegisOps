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
      className="rounded-lg border border-red-200 bg-red-50 p-6 text-center"
    >
      <p className="text-sm font-medium text-red-800">{title}</p>
      {message ? (
        <p className="mt-1 text-sm text-red-700">{message}</p>
      ) : null}
    </div>
  );
}
