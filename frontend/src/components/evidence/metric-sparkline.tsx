/**
 * A tiny inline chart for metric evidence. If the payload has numeric
 * baseline/peak values, it renders a stylized spike so metric evidence reads as
 * telemetry rather than raw JSON. Falls back to nothing if the shape is unknown.
 */
export function MetricSparkline({
  payload,
}: {
  payload: Record<string, unknown>;
}) {
  const baseline = Number(payload.baseline);
  const peak = Number(payload.peak);
  if (!Number.isFinite(baseline) || !Number.isFinite(peak) || peak <= baseline) {
    return null;
  }

  // Build a small series: flat baseline, sharp rise to peak, slight settle.
  const series = [baseline, baseline, baseline, peak, peak * 0.95, peak * 0.9];
  const w = 160;
  const h = 40;
  const max = Math.max(...series);
  const min = Math.min(...series);
  const range = max - min || 1;
  const pts = series
    .map((v, i) => {
      const x = (i / (series.length - 1)) * w;
      const y = h - ((v - min) / range) * h;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const fmt = (n: number) =>
    n < 1 ? `${(n * 100).toFixed(1)}%` : n.toLocaleString();

  return (
    <div className="mt-2 flex items-center gap-3">
      <svg
        width={w}
        height={h}
        viewBox={`0 0 ${w} ${h}`}
        className="overflow-visible"
        role="img"
        aria-label={`Metric spike from ${fmt(baseline)} to ${fmt(peak)}`}
      >
        <polyline
          points={pts}
          fill="none"
          stroke="#ef4444"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      </svg>
      <div className="text-xs text-slate-500">
        <div>
          baseline <span className="font-medium text-slate-700">{fmt(baseline)}</span>
        </div>
        <div>
          peak <span className="font-medium text-red-600">{fmt(peak)}</span>
        </div>
      </div>
    </div>
  );
}
