// Role: React Query hook for GET /api/lines
// Author: Dennies Bor

import { useQuery } from "@tanstack/react-query";
import { fetchLines } from "../lib/api.js";
import { DEFAULT_SIMPLIFY } from "../lib/constants.js";

/** Returns { data, isPending, isError } for the lines FeatureCollection. */
export function useLines(hazard) {
  return useQuery({
    queryKey: ["lines", hazard ?? null],
    queryFn: () => fetchLines(hazard, DEFAULT_SIMPLIFY),
  });
}
