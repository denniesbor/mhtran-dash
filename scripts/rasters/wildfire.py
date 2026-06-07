# scripts/rasters/wildfire.py
# Role: build the wildfire hazard potential raster overlay
# Author: Dennies Bor
# Source: viz/wildfire_hazard.py — FIRE_NORM = LogNorm(vmin=50, vmax=18176)
#         units: USFS WHP 2023 continuous score (dimensionless)
#         Source raster: whp2023_cnt_conus.tif (11283×17372, EPSG:5070)

from pathlib import Path

from matplotlib.colors import LogNorm

from rasters.base import (
    assert_crs,
    apply_colormap,
    load_large,
    reproject_to_albers,
    save_png,
    write_sidecar,
)
from colormaps.paper import WILDFIRE_CMAP

SOURCE = Path("/data/archives/nfs/multi-hazard/data/hazards/wildfire/Data/whp2023_GeoTIF/whp2023_cnt_conus.tif")
OUTPUT_PNG = Path("../web/public/rasters/wildfire.png")
OUTPUT_META = Path("../web/public/rasters/wildfire.json")

HAZARD = "wildfire"
UNITS = "WHP 2023 continuous score"
# Paper: LogNorm(vmin=50, vmax=18176); CB_TICKS=[50,200,500,2000,18000].
# vmin=50 masks near-zero background noise — only meaningful WHP shown.
VMIN, VMAX = 50.0, 18176.0


def build() -> None:
    # Full raster is ~196M pixels; load_large downsamples to ≤4M pixels.
    array, transform, crs, nodata = load_large(SOURCE)
    assert_crs(crs, expected_epsg=5070)
    array = reproject_to_albers(array, transform, crs)
    # Mask WHP scores below the paper's display threshold.
    import numpy as np
    array[array < VMIN] = np.nan
    rgba = apply_colormap(
        array, WILDFIRE_CMAP, VMIN, VMAX, nodata, norm=LogNorm(vmin=VMIN, vmax=VMAX)
    )
    save_png(rgba, OUTPUT_PNG)
    write_sidecar(
        OUTPUT_META,
        {
            "hazard": HAZARD,
            "units": UNITS,
            "vmin": VMIN,
            "vmax": VMAX,
            "colormap": WILDFIRE_CMAP.name,
            "source_file": SOURCE.name,
            "norm": "log",
        },
            cmap=WILDFIRE_CMAP,
    )
