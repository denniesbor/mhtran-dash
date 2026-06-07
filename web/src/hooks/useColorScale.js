// Role: memoized color scale shared between layer and legend
// Author: Dennies Bor

import { useMemo } from "react";
import { buildColorScale } from "../lib/colorScale.js";

/** Returns a D3 scale for the given features and hazard, stable across renders. */
export function useColorScale(features, hazard) {
  return useMemo(
    () => buildColorScale(features ?? [], hazard),
    [features, hazard],
  );
}
