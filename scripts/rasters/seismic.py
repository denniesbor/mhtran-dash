# scripts/rasters/seismic.py
# Role: build the seismic hazard raster overlay from USGS SA contour polygons
# Author: Dennies Bor
# Source: viz/seismic_hazard.py — SEIS_NORM = LogNorm(vmin=0.01, vmax=1.0)
#         units: SA(0.2s) in g, 2% probability of exceedance in 50 years (2475-yr RP)
#         B/C site class (Vs30 = 760 m/s, firm rock)
#
# Method: rasterize USGS 2023 hazard contour polygons (US_SA0P2_2Pct50Yrs_BC_poly.shp)
#   to the CONUS 5070 grid. Each polygon band has low_cont/high_cont SA values (g);
#   we burn high_cont so higher-hazard bands overwrite lower ones where they overlap.

from pathlib import Path

import numpy as np
import rasterio.features
from matplotlib.colors import LogNorm
from rasterio.crs import CRS
from rasterio.transform import from_bounds

from rasters.base import apply_colormap, save_png, write_sidecar
from colormaps.paper import SEISMIC_CMAP

SOURCE = Path("/data/archives/nfs/multi-hazard/data/hazards/seismic/pga_bc/US_SA0P2_2Pct50Yrs_BC_poly.shp")
OUTPUT_PNG = Path("../web/public/rasters/seismic.png")
OUTPUT_META = Path("../web/public/rasters/seismic.json")

HAZARD = "seismic"
UNITS = "SA(0.2s) in g, 2%/50yr (2475-yr RP), B/C site class"
# Paper: LogNorm(vmin=0.01, vmax=1.0); CB_TICKS=[0.01, 0.1, 1.0].
VMIN, VMAX = 0.01, 1.0

_CONUS_BBOX = (-2400000, 200000, 2300000, 3200000)
_W, _H = 1920, 1200


def build() -> None:
    import geopandas as gpd

    gdf = gpd.read_file(SOURCE)

    # high_cont is stored as string in this USGS shapefile — coerce to float.
    gdf["sa_val"] = gpd.pd.to_numeric(gdf["high_cont"], errors="coerce")
    gdf = gdf.dropna(subset=["sa_val", "geometry"])

    # Reproject to EPSG:5070 for direct alignment with the output grid.
    gdf = gdf.to_crs("EPSG:5070")

    transform = from_bounds(*_CONUS_BBOX, _W, _H)

    # Sort ascending so higher SA polygons overwrite lower ones during burn.
    gdf = gdf.sort_values("sa_val")
    shapes = [
        (geom.__geo_interface__, float(val))
        for geom, val in zip(gdf.geometry, gdf["sa_val"])
        if geom is not None
    ]

    sa_grid = rasterio.features.rasterize(
        shapes,
        out_shape=(_H, _W),
        transform=transform,
        fill=0.0,
        dtype=np.float32,
    )
    # Zero fill = no data (outside any contour polygon).
    sa_grid[sa_grid == 0] = np.nan
    # Mask below display threshold — very low-hazard interior is transparent.
    sa_grid[sa_grid < VMIN] = np.nan

    rgba = apply_colormap(
        sa_grid, SEISMIC_CMAP, VMIN, VMAX, nodata=None,
        norm=LogNorm(vmin=VMIN, vmax=VMAX),
    )
    save_png(rgba, OUTPUT_PNG)
    write_sidecar(
        OUTPUT_META,
        {
            "hazard": HAZARD,
            "units": UNITS,
            "vmin": VMIN,
            "vmax": VMAX,
            "colormap": SEISMIC_CMAP.name,
            "source_file": SOURCE.name,
            "norm": "log",
        },
            cmap=SEISMIC_CMAP,
    )
