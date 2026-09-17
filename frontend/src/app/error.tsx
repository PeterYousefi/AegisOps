"use client";

import { useEffect } from "react";
import Link from "next/link";
import { AlertTriangle } from "lucide-react";

/**
 * Root error boundary. Renders a friendly, recoverable screen instead of the
 * raw "Application error" overlay when a client-side exception occurs (for
 * example, if the backend API is unreachable).
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log for debugging; never surface raw internals to the user.
    console.error(error);
  }, [error]);

  return (
    <div className="mx-auto flex min-h-screen max-w-lg flex-col items-center justify-center p-6 text-center">
      <AlertTriangle className="h-8 w-8 text-red-500" aria-hidden />
      <h1 className="mt-4 text-xl font-semibold text-slate-900">
        Something went wrong
      </h1>
      <p className="mt-2 text-sm text-slate-600">
        The app hit an unexpected error. If you just started the frontend, make
        sure the backend API is running (see the README) and try again.
      </p>
      <div className="mt-6 flex gap-3">
        <button
          type="button"
          onClick={reset}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
        >
          Try again
        </button>
        <Link
          href="/incidents"
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
        >
          Go to incidents
        </Link>
      </div>
    </div>
  );
}
