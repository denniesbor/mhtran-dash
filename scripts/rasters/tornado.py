# scripts/rasters/tornado.py
# Role: build the tornado track density raster overlay
# Author: Dennies Bor
# Source: viz/tornado_hazard.py — TORN_CMAP_BG grey density background
#         units: tornado tracks per year per grid cell (annualised 1950–2024)
#
# Method: bin SPC tornado track centroids (1950–2024, n=71 813) into the
#   1920×1200 CONUS grid, apply Gaussian smoothing (~100 km sigma), then
#   annualise by dividing by the 75-year record length. Matches the paper's
#   approach of KDE-based density smoothing.

from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter

from rasters.base import apply_colormap, save_png, write_sidecar
from colormaps.paper import TORNADO_CMAP

SOURCE = Path("/data/archives/nfs/multi-hazard/data/hazards/tornado/1950-2024-torn-aspath/1950-2024-torn-aspath.shp")
OUTPUT_PNG = Path("../web/public/rasters/tornado.png")
OUTPUT_META = Path("../web/public/rasters/tornado.json")

HAZARD = "tornado"
UNITS = "tornado tracks/yr per grid cell (annualised 1950–2024)"

_CONUS_BBOX = (-2400000, 200000, 2300000, 3200000)
_W, _H = 1920, 1200
_YEARS = 2024 - 1950 + 1  # 75 years


def build() -> None:
    import geopandas as gpd

    gdf = gpd.read_file(SOURCE)
    gdf = gdf.to_crs("EPSG:5070")

    # Centroid of each track path (representative location per tornado).
    centroids = gdf.geometry.centroid
    xs = centroids.x.values
    ys = centroids.y.values

    left, bottom, right, top = _CONUS_BBOX

    valid = np.isfinite(xs) & np.isfinite(ys) & (xs >= left) & (xs <= right) & (ys >= bottom) & (ys <= top)
    xs, ys = xs[valid], ys[valid]

    # Count tracks per cell on an H×W grid.
    # histogram2d rows=y (bottom→top), flip to image coords (top→bottom).
    counts, _, _ = np.histogram2d(
        ys, xs,
        bins=[_H, _W],
        range=[[bottom, top], [left, right]],
    )
    counts = np.flipud(counts).astype(np.float32)

    # Gaussian smooth — sigma=12 cells ≈ 12 × (4700 m cell width) ≈ 56 km,
    # sufficient to spread individual tracks into a legible density surface.
    density = gaussian_filter(counts, sigma=12)

    # Annualise.
    density_per_year = density / _YEARS

    # Mask near-zero cells — keeps non-tornado regions transparent.
    threshold = np.nanpercentile(density_per_year[density_per_year > 0], 5)
    density_per_year[density_per_year < threshold] = np.nan

    vmax = float(np.nanpercentile(density_per_year[~np.isnan(density_per_year)], 99))
    vmin = float(threshold)

    rgba = apply_colormap(density_per_year, TORNADO_CMAP, vmin, vmax, nodata=None)
    save_png(rgba, OUTPUT_PNG)
    write_sidecar(
        OUTPUT_META,
        {
            "hazard": HAZARD,
            "units": UNITS,
            "vmin": round(vmin, 6),
            "vmax": round(vmax, 6),
            "colormap": TORNADO_CMAP.name,
            "source_file": SOURCE.name,
            "norm": "linear",
            "sigma_cells": 12,
            "record_years": _YEARS,
        },
            cmap=TORNADO_CMAP,
    )
