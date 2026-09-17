/** Simple confidence bar for an assessment (0–1). */
export function ConfidenceMeter({ score }: { score: number }) {
  const pct = Math.round(Math.max(0, Math.min(1, score)) * 100);
  const color =
    pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-2 w-32 overflow-hidden rounded-full bg-gray-200"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="AI confidence"
      >
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm text-gray-700">{pct}% confidence</span>
    </div>
  );
}
