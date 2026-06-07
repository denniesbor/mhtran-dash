# scripts/rasters/wind.py
# Role: build the tropical cyclone maximum wind speed raster overlay
# Author: Dennies Bor
# Source: viz/wind_hazard.py — WIND_NORM = Normalize(vmin=20, vmax=55) in m/s
#         units: maximum TC wind speed (mph) from hurr_maxwind_10km.tif
#         Note: source raster is in mph; paper uses county-level m/s data for
#         TC exceedance figures, but the continuous raster covers the same
#         physical phenomenon. WIND_CMAP (blue sequential) is shared.

from pathlib import Path

from rasters.base import (
    assert_crs,
    apply_colormap,
    load,
    reproject_to_albers,
    save_png,
    write_sidecar,
)
from colormaps.paper import WIND_CMAP

SOURCE = Path("/data/archives/nfs/multi-hazard/data/hazards/hurricane/processed/hurr_maxwind_10km.tif")
OUTPUT_PNG = Path("../web/public/rasters/wind.png")
OUTPUT_META = Path("../web/public/rasters/wind.json")

HAZARD = "wind"
UNITS = "max TC wind speed (mph)"
# Source range: 35–160 mph. Display from Cat-1 onset (74 mph) to Cat-5 (160 mph)
# so interior CONUS (sub-tropical-storm) is masked as nodata — only coastal
# hurricane-exposed areas receive colour.
VMIN, VMAX = 74.0, 160.0


def build() -> None:
    import numpy as np

    array, transform, crs, nodata = load(SOURCE)
    assert_crs(crs, expected_epsg=5070)
    array = reproject_to_albers(array, transform, crs)
    # Mask cells below Cat-1 onset — keeps interior US transparent.
    array[array < VMIN] = np.nan
    rgba = apply_colormap(array, WIND_CMAP, VMIN, VMAX, nodata)
    save_png(rgba, OUTPUT_PNG)
    write_sidecar(
        OUTPUT_META,
        {
            "hazard": HAZARD,
            "units": UNITS,
            "vmin": VMIN,
            "vmax": VMAX,
            "colormap": WIND_CMAP.name,
            "source_file": SOURCE.name,
            "norm": "linear",
        },
            cmap=WIND_CMAP,
    )
