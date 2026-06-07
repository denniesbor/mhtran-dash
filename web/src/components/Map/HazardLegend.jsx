// Role: horizontal gradient legend for the active EAD color scale
// Author: Dennies Bor

import { HAZARD_LABELS } from "../../lib/constants.js";
import { NULL_COLOR } from "../../lib/colorScale.js";

const fmt = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
  notation: "compact",
  compactDisplay: "short",
});

function scaleToGradient(colorScale) {
  // Sample the scale at 14 points to build a smooth CSS gradient.
  // colorScale.domain() returns [0, p95]; we walk the full interpolator range.
  const steps = 14;
  const stops = Array.from({ length: steps }, (_, i) => {
    const t = i / (steps - 1);
    const [lo, hi] = colorScale.domain();
    return `${colorScale(lo + t * (hi - lo))} ${(t * 100).toFixed(1)}%`;
  });
  return `linear-gradient(to right, ${stops.join(", ")})`;
}

/** Floating bottom-right legend card. Hidden when no data is loaded yet. */
export default function HazardLegend({ colorScale, hazard }) {
  // Fallback scale (no data) has no .domain() method — nothing to show.
  if (!colorScale || typeof colorScale.domain !== "function") return null;

  const [, p95] = colorScale.domain();
  const gradient = scaleToGradient(colorScale);
  const label = HAZARD_LABELS[hazard] ?? hazard;

  return (
    <div className="absolute bottom-4 right-4 z-10 bg-white border border-line rounded-lg shadow-md px-3 pt-2 pb-3 w-52">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs font-medium text-ink">
          {label} — EAD
        </span>
        <span className="text-[10px] text-ink-muted">$/yr</span>
      </div>

      {/* gradient bar */}
      <div
        className="h-2.5 rounded-sm w-full"
        style={{ background: gradient }}
      />

      {/* tick labels */}
      <div className="flex justify-between mt-1">
        <span className="text-[10px] text-ink-muted">$0</span>
        <span className="text-[10px] text-ink-muted">
          ≥ {fmt.format(p95)}
          <span className="opacity-60"> (p95)</span>
        </span>
      </div>

      {/* null indicator */}
      <div className="flex items-center gap-1.5 mt-2">
        <div
          className="w-3 h-3 rounded-sm shrink-0"
          style={{ background: NULL_COLOR }}
        />
        <span className="text-[10px] text-ink-muted">
          Outside EDR scope
        </span>
      </div>
    </div>
  );
}
