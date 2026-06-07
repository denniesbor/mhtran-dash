# api/src/mhtran_api/seeds/paths.py
# Role: filesystem paths to research data inputs
# Author: Dennies Bor
# Description: single source of truth for parquet locations; raises if the
#              expected file is missing so seeds fail at startup, not mid-run.

from pathlib import Path

DATA_ROOT = Path("/data/multi-hazard/data")
NETWORK_DIR = DATA_ROOT / "network"
HOTSPOTS_DIR = DATA_ROOT / "hotspots"

SUBS_NETWORK = NETWORK_DIR / "subs.parquet"
SUBS_EDR = HOTSPOTS_DIR / "subs_edr.parquet"
SUBS_COST = HOTSPOTS_DIR / "subs_cost.parquet"

SUBS_GEOMAG_100 = HOTSPOTS_DIR / "affected_subs_geomag_100yr.parquet"
SUBS_GEOMAG_250 = HOTSPOTS_DIR / "affected_subs_geomag_250yr.parquet"

SUBS_HAZARD_FILES = {
    "flood": HOTSPOTS_DIR / "subs_flood.parquet",
    "seismic": HOTSPOTS_DIR / "subs_seismic.parquet",
    "landslide": HOTSPOTS_DIR / "subs_landslide.parquet",
    "wildfire": HOTSPOTS_DIR / "subs_wildfire.parquet",
    "lightning": HOTSPOTS_DIR / "subs_lightning.parquet",
    "wind": HOTSPOTS_DIR / "subs_wind.parquet",
    "hail": HOTSPOTS_DIR / "subs_hail.parquet",
    "tornado": HOTSPOTS_DIR / "subs_tornado.parquet",
    "fzg": HOTSPOTS_DIR / "subs_fzg.parquet",
}

LINES_NETWORK = NETWORK_DIR / "lines.parquet"
LINES_EDR = HOTSPOTS_DIR / "lines_edr.parquet"
LINES_COST = HOTSPOTS_DIR / "lines_cost.parquet"
LINES_FLOOD = HOTSPOTS_DIR / "lines_flood.parquet"


def assert_inputs_present() -> None:
    missing = [str(p) for p in [SUBS_NETWORK, SUBS_EDR, SUBS_COST] if not p.exists()]
    missing += [str(p) for p in SUBS_HAZARD_FILES.values() if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing required seed inputs: {missing}")


def assert_lines_inputs_present() -> None:
    missing = [str(p) for p in [LINES_NETWORK, LINES_EDR, LINES_COST, LINES_FLOOD]
               if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing required lines seed inputs: {missing}")