// Role: fetch helpers — all API calls go through here
// Author: Dennies Bor

const BASE = import.meta.env.VITE_API_BASE_URL ?? "";

/** Fetch GeoJSON FeatureCollection from /api/substations. */
export async function fetchSubstations(hazard) {
  const url = new URL(`${BASE}/api/substations`, window.location.origin);
  if (hazard) url.searchParams.set("hazard", hazard);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`/api/substations ${res.status}`);
  return res.json();
}

/** Fetch GeoJSON FeatureCollection from /api/lines with forced simplification. */
export async function fetchLines(hazard, simplify = 0.01) {
  const url = new URL(`${BASE}/api/lines`, window.location.origin);
  if (hazard) url.searchParams.set("hazard", hazard);
  url.searchParams.set("simplify", simplify);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`/api/lines ${res.status}`);
  return res.json();
}
