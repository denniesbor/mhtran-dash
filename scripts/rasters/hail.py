# scripts/rasters/hail.py
# Role: build the annual hail rate raster overlay
# Author: Dennies Bor
# Source: viz/hail_hazard.py — HAIL_NORM = LogNorm(vmin=0.01, vmax=3.0)
#         units: annual hail events per km², derived from SPC storm reports

from pathlib import Path

from matplotlib.colors import LogNorm

from rasters.base import (
    assert_crs,
    apply_colormap,
    load,
    reproject_to_albers,
    save_png,
    write_sidecar,
)
from colormaps.paper import HAIL_CMAP

SOURCE = Path("/data/archives/nfs/multi-hazard/data/hazards/hail/processed/hail_annual_rate_10km.tif")
OUTPUT_PNG = Path("../web/public/rasters/hail.png")
OUTPUT_META = Path("../web/public/rasters/hail.json")

HAZARD = "hail"
UNITS = "annual hail events/km²"
# Paper: LogNorm(vmin=0.01, vmax=3.0); data max ~2.9, concentrated in Great Plains.
VMIN, VMAX = 0.01, 3.0


def build() -> None:
    array, transform, crs, nodata = load(SOURCE)
    assert_crs(crs, expected_epsg=5070)
    array = reproject_to_albers(array, transform, crs)
    rgba = apply_colormap(
        array, HAIL_CMAP, VMIN, VMAX, nodata, norm=LogNorm(vmin=VMIN, vmax=VMAX)
    )
    save_png(rgba, OUTPUT_PNG)
    write_sidecar(
        OUTPUT_META,
        {
            "hazard": HAZARD,
            "units": UNITS,
            "vmin": VMIN,
            "vmax": VMAX,
            "colormap": HAIL_CMAP.name,
            "source_file": SOURCE.name,
            "norm": "log",
        },
            cmap=HAIL_CMAP,
    )
