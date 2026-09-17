import type { LucideIcon } from "lucide-react";

/** A small summary statistic card for the dashboard header strip. */
export function StatCard({
  label,
  value,
  icon: Icon,
  tone = "default",
}: {
  label: string;
  value: number;
  icon: LucideIcon;
  tone?: "default" | "critical" | "warning" | "success";
}) {
  const toneStyles: Record<string, string> = {
    default: "text-slate-500",
    critical: "text-red-600",
    warning: "text-amber-600",
    success: "text-green-600",
  };
  return (
    <div className="card flex items-center gap-3 p-4">
      <span className={`${toneStyles[tone]}`}>
        <Icon className="h-5 w-5" aria-hidden />
      </span>
      <div>
        <div className="text-2xl font-semibold leading-none text-slate-900">
          {value}
        </div>
        <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
          {label}
        </div>
      </div>
    </div>
  );
}
