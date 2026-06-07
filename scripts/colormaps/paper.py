# scripts/colormaps/paper.py
# Role: colormap definitions extracted from viz/ paper figures
# Author: Dennies Bor
# Description: reproduces the exact colormaps used in the mhtran paper so the
#   dashboard raster overlays match the published figures.

from matplotlib.colors import LinearSegmentedColormap

# Source: viz/lightning_hazard.py — NASA LIS/OTD flash-rate figure
# Stops reproduce the warm-yellow to deep-red ramp from the paper.
LIGHTNING_CMAP = LinearSegmentedColormap.from_list(
    "lightning",
    ["#f7f4bc", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#8c2d04"],
    N=256,
)
LIGHTNING_CMAP.set_bad(alpha=0)

# Source: viz/flood_hazard.py — Aqueduct 100-yr flood depth figure
# Blue-purple sequential ramp; paper uses LogNorm(0.1, 30) on depth (m).
FLOOD_CMAP = LinearSegmentedColormap.from_list(
    "flood_purple",
    ["#deebf7", "#dadaeb", "#9e9ac8", "#6a51a3", "#3f007d"],
    N=256,
)
FLOOD_CMAP.set_bad(alpha=0)

# Source: viz/seismic_hazard.py — USGS SA(0.2s) 2%/50yr figure
SEISMIC_CMAP = LinearSegmentedColormap.from_list(
    "seis",
    ["#ffffff", "#fee8c8", "#fdbb84", "#e34a33", "#7f0000"],
    N=256,
)
SEISMIC_CMAP.set_bad(alpha=0)

# Source: viz/landslide_hazard.py — USGS landslide susceptibility figure
LANDSLIDE_CMAP = LinearSegmentedColormap.from_list(
    "landslide",
    ["#f5f5f5", "#d9f0a3", "#addd8e", "#78c679", "#31a354", "#006837", "#4d2600"],
    N=256,
)
LANDSLIDE_CMAP.set_bad(alpha=0)

# Source: viz/wildfire_hazard.py — USFS WHP 2023 continuous figure
WILDFIRE_CMAP = LinearSegmentedColormap.from_list(
    "fire",
    ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026", "#67000d"],
    N=256,
)
WILDFIRE_CMAP.set_bad(alpha=0)

# Source: viz/wind_hazard.py — TC wind exceedance figure (blue sequential)
WIND_CMAP = LinearSegmentedColormap.from_list(
    "wind",
    ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#084594", "#00008b"],
    N=256,
)
WIND_CMAP.set_bad(alpha=0)

# Source: viz/hail_hazard.py — annual hail rate figure
HAIL_CMAP = LinearSegmentedColormap.from_list(
    "hail",
    ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#084594"],
    N=256,
)
HAIL_CMAP.set_bad(alpha=0)

# Source: viz/tornado_hazard.py — tornado track density background
TORNADO_CMAP = LinearSegmentedColormap.from_list(
    "tornado_bg",
    ["#f7f7f7", "#d9d9d9", "#969696", "#525252", "#252525"],
    N=256,
)
TORNADO_CMAP.set_bad(alpha=0)

# Source: C-SWIM viz/plots.py — geoelectric field maps.
# Uses magma (not reversed) trimmed 0.1→0.95 so low hazard = dark purple/cool
# and high hazard = bright yellow/warm, matching the high=vivid convention of
# the other hazard colormaps (lightning, wildfire, seismic).
import matplotlib.cm as _mcm
import numpy as _np
_base = _mcm.get_cmap("magma")
GEOMAG_CMAP = LinearSegmentedColormap.from_list(
    "geomag",
    [_base(v) for v in _np.linspace(0.1, 0.95, 256)],
    N=256,
)
GEOMAG_CMAP.set_bad(alpha=0)
del _base, _mcm, _np
