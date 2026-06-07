# scripts/rasters/geomag.py
# Role: build geomagnetic geoelectric/magnetic field raster overlays
# Author: Dennies Bor
# Source: C-SWIM data/statistical_analysis/geomagnetic_data_return_periods.h5
#         predictions/E/{rp}_year → (1616,) V/km geoelectric field per MT site
#         predictions/B/{rp}_year → (1616,) nT magnetic field per MT site
#         sites/mt_sites/coordinates → (1616, 2) [lat, lon] per site
#         Viz ref: C-SWIM econ/scripts/l_prepr_data.py load_and_process_gic_data()
#                  viz/plot_utils.py generate_grid_and_mask() — griddata linear interp
#
# Produces 4 PNGs: geomag_E_100, geomag_E_250, geomag_B_100, geomag_B_250
# Default geomag.png = geomag_E_100.png (copied)

from pathlib import Path

import numpy as np
from matplotlib.colors import LogNorm
from rasterio.crs import CRS
from rasterio.transform import from_bounds

from rasters.base import apply_colormap, reproject_to_albers, save_png, write_sidecar
from colormaps.paper import GEOMAG_CMAP

H5_FILE = Path("/data/archives/nfs/c-swim/data/statistical_analysis/geomagnetic_data_return_periods.h5")
OUT_DIR = Path("../web/public/rasters")
_NERC_SHP = Path("/data/archives/nfs/multi-hazard/data/c-swim/nerc/electricity_operators.shp")

# E-field display range (V/km) — HDF5 100yr: min=0.01, max=25 V/km; 250yr up to ~45
E_VMIN, E_VMAX = 0.05, 25.0
# B-field display range (nT) — HDF5 100yr: min=407, mean=984, max=2492 nT
B_VMIN, B_VMAX = 200.0, 2500.0

_GRID_LON, _GRID_LAT = 800, 500


def _apply_conus_mask(
    grid_z: np.ndarray,
    left: float,
    top: float,
    right: float,
    bottom: float,
    width: int,
    height: int,
) -> None:
    """Set grid cells outside the CONUS boundary to NaN, in-place."""
    import geopandas as gpd
    from rasterio.features import geometry_mask
    from rasterio.transform import from_bounds as tfb
    from shapely.ops import unary_union

    gdf = gpd.read_file(_NERC_SHP)
    conus_geom = unary_union(gdf.geometry)
    transform = tfb(left, bottom, right, top, width, height)
    outside = geometry_mask([conus_geom], out_shape=(height, width), transform=transform)
    grid_z[outside] = np.nan


def _build_variant(
    field_type: str,
    return_period: int,
    vmin: float,
    vmax: float,
    units: str,
) -> None:
    import h5py
    from scipy.interpolate import griddata
    from scipy.ndimage import gaussian_filter

    with h5py.File(H5_FILE, "r") as f:
        # coordinates: (1616, 2) — column 0 = lat, column 1 = lon
        mt_coords = f["sites/mt_sites/coordinates"][:]
        field_values = f[f"predictions/{field_type}/{return_period}_year"][:]

    lats = mt_coords[:, 0]
    lons = mt_coords[:, 1]

    lon_min, lon_max = -130.0, -60.0
    lat_min, lat_max = 20.0, 55.0

    # lat goes top→bottom (lat_max→lat_min) so row-0 = northernmost pixel,
    # matching rasterio's convention used by from_bounds and reproject_to_albers.
    grid_lons, grid_lats = np.meshgrid(
        np.linspace(lon_min, lon_max, _GRID_LON),
        np.linspace(lat_max, lat_min, _GRID_LAT),
    )

    # griddata with (lon, lat) points — same convention as C-SWIM generate_grid_and_mask
    points = np.column_stack([lons, lats])
    grid_z = griddata(points, field_values, (grid_lons, grid_lats), method="linear")
    grid_z = grid_z.astype(np.float32)

    # Mask to CONUS before smoothing so Gaussian doesn't bleed values across the US border.
    _apply_conus_mask(grid_z, lon_min, lat_max, lon_max, lat_min, _GRID_LON, _GRID_LAT)

    # Log-space Gaussian smoothing erases sharp Delaunay triangulation edges while
    # preserving the order-of-magnitude structure of the E/B field.
    valid_mask = np.isfinite(grid_z) & (grid_z > 0)
    log_z = np.where(valid_mask, np.log(np.clip(grid_z, 1e-9, None)), np.nan)
    log_filled = np.where(valid_mask, log_z, 0.0)
    smooth_log = gaussian_filter(log_filled, sigma=4)
    weight = gaussian_filter(valid_mask.astype(np.float32), sigma=4)
    with np.errstate(invalid="ignore", divide="ignore"):
        smooth_log = np.where(weight > 0.05, smooth_log / weight, np.nan)
    grid_z = np.where(np.isfinite(smooth_log), np.exp(smooth_log).astype(np.float32), np.nan)

    grid_z[grid_z < vmin] = np.nan

    src_transform = from_bounds(lon_min, lat_min, lon_max, lat_max, _GRID_LON, _GRID_LAT)
    src_crs = CRS.from_epsg(4326)
    array_5070 = reproject_to_albers(grid_z, src_transform, src_crs)

    rgba = apply_colormap(
        array_5070,
        GEOMAG_CMAP,
        vmin,
        vmax,
        nodata=None,
        norm=LogNorm(vmin=vmin, vmax=vmax),
    )

    stem = f"geomag_{field_type}_{return_period}"
    save_png(rgba, OUT_DIR / f"{stem}.png")
    write_sidecar(
        OUT_DIR / f"{stem}.json",
        {
            "hazard": "geomag",
            "field": field_type,
            "return_period_yr": return_period,
            "units": units,
            "vmin": vmin,
            "vmax": vmax,
            "colormap": GEOMAG_CMAP.name,
            "source_file": H5_FILE.name,
            "norm": "log",
        },
        cmap=GEOMAG_CMAP,
    )


def build() -> None:
    """Build all 4 geomag variants: E/B × 100yr/250yr."""
    _build_variant("E", 100, E_VMIN, E_VMAX, "geoelectric field (V/km), 100-yr RP")
    _build_variant("E", 250, E_VMIN, E_VMAX, "geoelectric field (V/km), 250-yr RP")
    _build_variant("B", 100, B_VMIN, B_VMAX, "magnetic field (nT), 100-yr RP")
    _build_variant("B", 250, B_VMIN, B_VMAX, "magnetic field (nT), 250-yr RP")

    import shutil
    shutil.copy(OUT_DIR / "geomag_E_100.png", OUT_DIR / "geomag.png")
    shutil.copy(OUT_DIR / "geomag_E_100.json", OUT_DIR / "geomag.json")
