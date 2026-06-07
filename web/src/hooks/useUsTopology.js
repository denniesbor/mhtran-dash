// Role: React Query hook for the US states TopoJSON
// Author: Dennies Bor

import { useQuery } from "@tanstack/react-query";

/**
 * Async-loads the us-atlas states-10m topology. Using dynamic import() so
 * Vite chunks it separately from the main bundle — the raw JSON is ~700 KB
 * and would otherwise block main-thread parse on every page load.
 */
export function useUsTopology() {
  return useQuery({
    queryKey: ["us-topology"],
    queryFn: () => import("us-atlas/states-10m.json").then((m) => m.default),
    staleTime: Infinity,
    gcTime: Infinity,
  });
}
