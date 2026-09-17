import { Inbox } from "lucide-react";

/** Reusable empty-state block for lists and panels with no content. */
export function EmptyState({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-dashed border-slate-300 bg-white/50 p-8 text-center">
      <Inbox className="h-6 w-6 text-slate-400" aria-hidden />
      <p className="mt-2 text-sm font-medium text-slate-900">{title}</p>
      {description ? (
        <p className="mt-1 max-w-sm text-sm text-slate-500">{description}</p>
      ) : null}
    </div>
  );
}
