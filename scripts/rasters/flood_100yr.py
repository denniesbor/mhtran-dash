# scripts/rasters/flood_100yr.py
# Role: build the 100-yr flood depth raster overlay (Aqueduct)
# Author: Dennies Bor

from pathlib import Path

from matplotlib.colors import LogNorm

import numpy as np

from rasters.base import (
    assert_crs,
    apply_colormap,
    load_conus_window,
    reproject_to_albers,
    save_png,
    write_sidecar,
)
from colormaps.paper import FLOOD_CMAP

# Source is global at 21600x43200 — load_conus_window clips and downsamples.
SOURCE = Path("/data/archives/nfs/multi-hazard/data/aqueduct/inunriver_historical_000000000WATCH_1980_rp00100.tif")
OUTPUT_PNG = Path("../web/public/rasters/flood.png")
OUTPUT_META = Path("../web/public/rasters/flood.json")

HAZARD = "flood"
UNITS = "depth (m), 100-yr return period"
# Paper figure uses LogNorm(vmin=0.1, vmax=30); data max is ~33 m.
VMIN, VMAX = 0.1, 30.0


def build() -> None:
    # Windowed read — global Aqueduct raster is ~3.7 GB uncompressed.
    array, transform, crs, nodata = load_conus_window(SOURCE)
    assert_crs(crs, expected_epsg=4326)
    array = reproject_to_albers(array, transform, crs)
    # Mask depths below 0.5 m — very shallow inundation is visually indistinct
    # and produces near-white blobs on the purple colormap (LogNorm low end).
    array[array < 0.5] = np.nan
    rgba = apply_colormap(
        array, FLOOD_CMAP, VMIN, VMAX, nodata, norm=LogNorm(vmin=VMIN, vmax=VMAX)
    )
    save_png(rgba, OUTPUT_PNG)
    write_sidecar(
        OUTPUT_META,
        {
            "hazard": HAZARD,
            "units": UNITS,
            "vmin": VMIN,
            "vmax": VMAX,
            "colormap": FLOOD_CMAP.name,
            "source_file": SOURCE.name,
            "norm": "log",
        },
            cmap=FLOOD_CMAP,
    )
