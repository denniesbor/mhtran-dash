// Role: React Query hook for GET /api/substations
// Author: Dennies Bor

import { useQuery } from "@tanstack/react-query";
import { fetchSubstations } from "../lib/api.js";

/** Returns { data, isPending, isError } for the substations FeatureCollection. */
export function useSubstations(hazard) {
  return useQuery({
    queryKey: ["substations", hazard ?? null],
    queryFn: () => fetchSubstations(hazard),
  });
}
