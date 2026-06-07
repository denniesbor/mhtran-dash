# scripts/rasters/lightning.py
# Role: build the lightning annual flash rate raster overlay
# Author: Dennies Bor

from pathlib import Path

from rasters.base import (
    assert_crs,
    apply_colormap,
    load,
    reproject_to_albers,
    save_png,
    write_sidecar,
)
from colormaps.paper import LIGHTNING_CMAP

SOURCE = Path("/data/archives/nfs/multi-hazard/data/hotspots/lightning_annual_rate_4326.tif")
OUTPUT_PNG = Path("../web/public/rasters/lightning.png")
OUTPUT_META = Path("../web/public/rasters/lightning.json")

HAZARD = "lightning"
UNITS = "flashes/km²/yr"
# Paper figure uses Normalize(vmin=0, vmax=33); p99 of the data is ~30.
VMIN, VMAX = 0.0, 33.0


def build() -> None:
    array, transform, crs, nodata = load(SOURCE)
    assert_crs(crs, expected_epsg=4326)
    array = reproject_to_albers(array, transform, crs)
    rgba = apply_colormap(array, LIGHTNING_CMAP, VMIN, VMAX, nodata)
    save_png(rgba, OUTPUT_PNG)
    write_sidecar(
        OUTPUT_META,
        {
            "hazard": HAZARD,
            "units": UNITS,
            "vmin": VMIN,
            "vmax": VMAX,
            "colormap": LIGHTNING_CMAP.name,
            "source_file": SOURCE.name,
            "norm": "linear",
        },
            cmap=LIGHTNING_CMAP,
    )
