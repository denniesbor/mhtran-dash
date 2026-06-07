# scripts/rasters/landslide.py
# Role: build the landslide susceptibility raster overlay
# Author: Dennies Bor
# Source: viz/landslide_hazard.py — LS_NORM = Normalize(vmin=0, vmax=81)
#         units: USGS Landslide Warning susceptibility index (0 = low, 81 = high)
#         CRS: EPSG:4269 (NAD83, degree-based — compatible with CONUS window load)

from pathlib import Path

from rasterio.warp import Resampling

from rasters.base import (
    apply_colormap,
    load_conus_window,
    reproject_to_albers,
    save_png,
    write_sidecar,
)
from colormaps.paper import LANDSLIDE_CMAP

SOURCE = Path("/data/archives/nfs/multi-hazard/data/hazards/landslide/lw_susc/lw_susc/lw_conus.tif")
OUTPUT_PNG = Path("../web/public/rasters/landslide.png")
OUTPUT_META = Path("../web/public/rasters/landslide.json")

HAZARD = "landslide"
UNITS = "susceptibility index (0–81)"
# Paper: Normalize(vmin=0, vmax=81); CB_TICKS=[0,20,40,60,81].
VMIN, VMAX = 0.0, 81.0


def build() -> None:
    # Source is EPSG:4269 (NAD83 degrees) — same spatial ref as 4326 for CONUS.
    # No assert_crs: 4269 vs 4326 differ only in datum, interchangeable here.
    import numpy as np

    array, transform, crs, nodata = load_conus_window(SOURCE)
    # load_conus_window uses bilinear downsampling on the int32 source which
    # produces fractional values. Round back to integer susceptibility levels
    # before reprojection so the output has at most 81 unique RGBA values.
    array = np.round(array).astype(np.float32)
    array = reproject_to_albers(array, transform, crs, resampling=Resampling.nearest)
    array = np.round(array).astype(np.float32)
    rgba = apply_colormap(array, LANDSLIDE_CMAP, VMIN, VMAX, nodata)
    save_png(rgba, OUTPUT_PNG)
    write_sidecar(
        OUTPUT_META,
        {
            "hazard": HAZARD,
            "units": UNITS,
            "vmin": VMIN,
            "vmax": VMAX,
            "colormap": LANDSLIDE_CMAP.name,
            "source_file": SOURCE.name,
            "norm": "linear",
        },
            cmap=LANDSLIDE_CMAP,
    )
