// Role: shared constants — hazard list, defaults
// Author: Dennies Bor

export const HAZARDS = [
  "flood",
  "seismic",
  "landslide",
  "wildfire",
  "lightning",
  "wind",
  "hail",
  "tornado",
  "fzg",
  "geomag",
];

/** Hazards available for transmission lines (geomag has no line-level EDR). */
export const LINE_HAZARDS = new Set(HAZARDS.filter((h) => h !== "geomag"));

export const DEFAULT_HAZARD = "flood";

/** Always passed to /api/lines to keep payload manageable (~4 MB vs 18 MB). */
export const DEFAULT_SIMPLIFY = 0.01;

/** Hazards that have a prebuilt raster PNG in web/public/rasters/. */
export const RASTER_HAZARDS = new Set(["lightning", "flood", "hail", "landslide", "wildfire", "wind", "seismic", "tornado", "geomag"]);

/** Human-readable label for each hazard key. */
export const HAZARD_LABELS = {
  flood:     "Flood",
  seismic:   "Seismic",
  landslide: "Landslide",
  wildfire:  "Wildfire",
  lightning: "Lightning",
  wind:      "Wind",
  hail:      "Hail",
  tornado:   "Tornado",
  fzg:       "Freeze",
  geomag:    "Geomag",
};
