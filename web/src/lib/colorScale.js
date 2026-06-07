// Role: pure color scale builder — (features, hazard) -> d3 scale
// Author: Dennies Bor

import * as d3 from "d3";

// Null-EAD features (outside EDR scope) — slate blue-grey, clearly distinct
// from the red damage scale so "no data" reads differently from "low risk".
export const NULL_COLOR = "#94a3b8";

/**
 * Build a sequential Reds scale for the given hazard column.
 *
 * COLOR CHOICE — ColorBrewer Reds:
 *   Reds (light-pink → deep-crimson) is perceptually clean on near-white
 *   backgrounds, unambiguous for damage-cost data, and matches the single-hue
 *   sequential palettes common in the paper figures. OrRd and YlOrRd were
 *   rejected: the yellow/orange low-end reads as "caution" rather than
 *   "low damage" and conflicts with the background colour.
 *   The interpolator is offset to t=0.15 so even the minimum exposed feature
 *   shows a visible light pink instead of near-white.
 *
 * DOMAIN DECISION — 95th percentile cap:
 *   EAD distributions are strongly right-skewed. Using the raw max compresses
 *   95% of features into the light end. The p95 cap spreads the bulk of the
 *   distribution across the full ramp; features above the cap clamp to deep red.
 *
 * LEGEND REQUIREMENT:
 *   HazardLegend.jsx MUST label the max tick "≥ p95" — never the raw max.
 */
export function buildColorScale(features, hazard) {
  if (!hazard) return () => NULL_COLOR;

  const key = `ead_${hazard}`;
  const values = features
    .map((f) => f.properties[key])
    .filter((v) => v != null && v > 0);

  if (values.length === 0) return () => NULL_COLOR;

  values.sort(d3.ascending);
  const p95 = d3.quantile(values, 0.95) ?? values[values.length - 1];

  return d3
    .scaleSequential()
    .domain([0, p95])
    .interpolator((t) => d3.interpolateReds(0.15 + t * 0.85))
    .clamp(true);
}
