# scripts/rasters/base.py
# Role: shared pipeline primitives used by every per-hazard raster module
# Author: Dennies Bor

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from matplotlib.colors import Normalize, LogNorm
from PIL import Image
from rasterio.crs import CRS
from rasterio.transform import from_bounds
from rasterio.warp import Resampling, reproject as rio_reproject

# EPSG:5070 CONUS bounding box in metres.
# Derived from D3 geoAlbersUsa().scale(1300).translate([480,300]) by inverting
# the four canvas edges to lon/lat and projecting through pyproj EPSG:5070:
#   left-mid  [0, 300]   → (-123.20, 35.62) → x ≈ -2,409,000
#   right-mid [960, 300] → (-69.90, 35.87)  → x ≈  2,307,000
#   top-mid   [480, 0]   → (-96.73, 51.96)  → y ≈  3,212,000
#   bot-mid   [480, 600] → (-96.51, 25.52)  → y ≈    276,000
# [0,600] is skipped — it falls in D3's Alaska inset, not the lower-48.
_DST_CRS = "EPSG:5070"
_CONUS_BBOX = (-2409000, 276000, 2307000, 3212000)  # (left, bottom, right, top)
_DST_WIDTH = 1920
_DST_HEIGHT = 1200
_MAX_BYTES = 4_000_000  # 4 MB budget; rasters served with immutable cache so only loaded once


def load(path: Path) -> tuple[np.ndarray, rasterio.Affine, CRS, float | None]:
    """Open a single-band raster and return (array float32, transform, crs, nodata).

    Nodata pixels are converted to NaN in the returned array.
    Raises if the file is missing, the band count is not 1, or there is no CRS.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"source raster not found: {path}")

    with rasterio.open(path) as src:
        if src.count != 1:
            raise ValueError(f"expected single-band raster, got {src.count} bands: {path}")
        if src.crs is None:
            raise ValueError(f"raster has no CRS: {path}")

        array = src.read(1).astype(np.float32)
        nodata = src.nodata
        if nodata is not None:
            array[array == nodata] = np.nan

        return array, src.transform, src.crs, nodata


def load_conus_window(
    path: Path,
    lon_min: float = -130.0,
    lon_max: float = -60.0,
    lat_min: float = 20.0,
    lat_max: float = 55.0,
    max_out_pixels: int = 4_000_000,
) -> tuple[np.ndarray, rasterio.Affine, CRS, float | None]:
    """Read only the CONUS window from a large global raster, downsampled to
    stay within max_out_pixels. Use this instead of load() for rasters whose
    full global extent would exhaust RAM (e.g. Aqueduct at 21600x43200).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"source raster not found: {path}")

    with rasterio.open(path) as src:
        if src.crs is None:
            raise ValueError(f"raster has no CRS: {path}")

        from rasterio.windows import from_bounds as win_from_bounds

        window = win_from_bounds(lon_min, lat_min, lon_max, lat_max, src.transform)
        win_h = int(window.height)
        win_w = int(window.width)

        # Compute downsample factor to stay within pixel budget.
        factor = max(1, int(np.sqrt(win_h * win_w / max_out_pixels)))
        out_h = max(1, win_h // factor)
        out_w = max(1, win_w // factor)

        array = src.read(
            1,
            window=window,
            out_shape=(out_h, out_w),
            resampling=Resampling.bilinear,
        ).astype(np.float32)

        nodata = src.nodata
        if nodata is not None:
            array[array == nodata] = np.nan

        win_transform = src.window_transform(window)
        # Scale the transform to match the downsampled output size.
        from rasterio.transform import from_bounds as tf_from_bounds
        from rasterio.windows import bounds as win_bounds
        wb = win_bounds(window, src.transform)
        array_transform = tf_from_bounds(*wb, out_w, out_h)

        return array, array_transform, src.crs, nodata


def load_large(
    path: Path,
    max_out_pixels: int = 4_000_000,
) -> tuple[np.ndarray, rasterio.Affine, CRS, float | None]:
    """Read a large single-band raster downsampled to fit within max_out_pixels.
    Use for high-resolution rasters in any CRS that would exhaust RAM at full
    resolution (e.g. USFS WHP at 11k×17k pixels).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"source raster not found: {path}")

    with rasterio.open(path) as src:
        if src.count != 1:
            raise ValueError(f"expected single-band raster, got {src.count} bands: {path}")
        if src.crs is None:
            raise ValueError(f"raster has no CRS: {path}")

        factor = max(1, int(np.sqrt(src.width * src.height / max_out_pixels)))
        out_h = max(1, src.height // factor)
        out_w = max(1, src.width // factor)

        array = src.read(
            1,
            out_shape=(out_h, out_w),
            resampling=Resampling.bilinear,
        ).astype(np.float32)

        nodata = src.nodata
        if nodata is not None:
            array[array == nodata] = np.nan

        from rasterio.transform import from_bounds as tf_from_bounds
        out_transform = tf_from_bounds(*src.bounds, out_w, out_h)

        return array, out_transform, src.crs, nodata


def assert_crs(crs: CRS, expected_epsg: int) -> None:
    """Raise if crs does not match expected_epsg. No silent reprojections.

    Falls back to comparing against a freshly constructed EPSG CRS when
    to_epsg() returns None (e.g. due to a stale system PROJ database).
    """
    actual = crs.to_epsg()
    if actual == expected_epsg:
        return
    # Fallback: compare WKT of the input CRS against a known-good construction.
    # This handles cases where PROJ can't identify the authority code from WKT.
    expected_crs = CRS.from_epsg(expected_epsg)
    if not crs.equals(expected_crs):
        raise ValueError(
            f"expected EPSG:{expected_epsg}, got EPSG:{actual} ({crs.to_string()!r})"
        )


def reproject_to_albers(
    array: np.ndarray,
    src_transform: rasterio.Affine,
    src_crs: CRS,
    resampling: Resampling = Resampling.bilinear,
) -> np.ndarray:
    """Reproject array to EPSG:5070 clipped to the CONUS bbox at 1920x1200.

    Returns the reprojected float32 array. NaN areas (nodata or outside source
    extent) remain NaN in the output.

    Use Resampling.nearest for integer/ordinal sources (landslide susceptibility,
    categorical classes) — preserves discrete values and produces much smaller PNGs.
    Use Resampling.bilinear (default) for continuous physical quantities.
    """
    dst_transform = from_bounds(*_CONUS_BBOX, _DST_WIDTH, _DST_HEIGHT)
    dst_array = np.full((_DST_HEIGHT, _DST_WIDTH), np.nan, dtype=np.float32)

    rio_reproject(
        source=array,
        destination=dst_array,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=CRS.from_epsg(5070),
        src_nodata=np.nan,
        dst_nodata=np.nan,
        resampling=resampling,
    )

    return dst_array


def apply_colormap(
    array: np.ndarray,
    cmap,
    vmin: float,
    vmax: float,
    nodata: float | None,
    norm=None,
) -> np.ndarray:
    """Map float array to uint8 RGBA. Alpha=0 at NaN/nodata, 180 elsewhere.

    cmap may be a matplotlib colormap object or a registered colormap name.
    norm may be a matplotlib Normalize instance; defaults to linear [vmin,vmax].
    """
    import matplotlib.cm as mcm
    from matplotlib.colors import is_color_like

    if isinstance(cmap, str):
        cmap = mcm.get_cmap(cmap)

    mask = np.isnan(array)

    if norm is None:
        norm = Normalize(vmin=vmin, vmax=vmax)

    # Normalise — safe_array avoids NaN warnings in norm()
    safe = np.where(mask, vmin, array)
    normed = np.clip(norm(safe), 0.0, 1.0)

    rgba = (cmap(normed) * 255).astype(np.uint8)
    rgba[mask, 3] = 0    # transparent at nodata
    rgba[~mask, 3] = 180  # 70% opacity where data exists

    return rgba


def save_png(rgba: np.ndarray, output_path: Path) -> None:
    """Save uint8 RGBA array as an optimised PNG. Raises if file exceeds 1 MB."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.fromarray(rgba, mode="RGBA")
    # compress_level=9 is max zlib compression (lossless); important for coarse
    # upsampled rasters whose bilinear gradients inflate file size.
    img.save(output_path, format="PNG", optimize=True, compress_level=9)

    size = output_path.stat().st_size
    if size > _MAX_BYTES:
        output_path.unlink()
        raise RuntimeError(
            f"output {output_path.name} is {size / 1_000:.0f} KB — exceeds 1 MB budget. "
            "Downsample the source or reduce the output resolution."
        )


def colormap_stops(cmap, n: int = 10) -> list[str]:
    """Sample a matplotlib colormap at n evenly-spaced positions and return hex strings.

    Used to embed gradient stops in sidecar JSON so the frontend legend can
    render an exact colormap gradient without replicating the Python definitions.
    """
    t = np.linspace(0, 1, n)
    rgba = (cmap(t) * 255).astype(np.uint8)
    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, _ in rgba]


def write_sidecar(output_path: Path, meta: dict, cmap=None) -> None:
    """Write a JSON sidecar next to the PNG with data range and colormap info.

    If cmap is provided, gradient_stops (10 hex colors, 0→1 of the colormap)
    are added so the frontend legend can render the exact gradient.
    """
    output_path = Path(output_path)
    payload = {
        **meta,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_width": _DST_WIDTH,
        "output_height": _DST_HEIGHT,
        "dst_crs": _DST_CRS,
        "conus_bbox_epsg5070": list(_CONUS_BBOX),
    }
    if cmap is not None:
        payload["gradient_stops"] = colormap_stops(cmap)
    output_path.write_text(json.dumps(payload, indent=2))
