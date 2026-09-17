import Link from "next/link";
import { Compass } from "lucide-react";

/** 404 page for unknown routes. */
export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-screen max-w-lg flex-col items-center justify-center p-6 text-center">
      <Compass className="h-8 w-8 text-slate-400" aria-hidden />
      <h1 className="mt-4 text-xl font-semibold text-slate-900">Page not found</h1>
      <p className="mt-2 text-sm text-slate-600">
        The page you are looking for does not exist.
      </p>
      <Link
        href="/incidents"
        className="mt-6 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
      >
        Go to incidents
      </Link>
    </div>
  );
}
