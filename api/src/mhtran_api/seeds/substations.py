# api/src/mhtran_api/seeds/substations.py
# Role: seed the substations table from research parquet outputs
# Author: Dennies Bor
# Description: joins network/subs (11,094 rows) with subs_cost, subs_edr,
#              and per-hazard intensity-measure parquets; writes via
#              GeoPandas to_postgis with truncate-and-append semantics.

import geopandas as gpd
import pandas as pd
from sqlalchemy import text

from mhtran_api.db import engine
from mhtran_api.models import Substation
from mhtran_api.seeds.paths import (
    SUBS_COST,
    SUBS_EDR,
    SUBS_GEOMAG_100,
    SUBS_GEOMAG_250,
    SUBS_HAZARD_FILES,
    SUBS_NETWORK,
    assert_inputs_present,
)

EXPECTED_NETWORK_ROWS = 11094
EXPECTED_EDR_ROWS = 6156

IDENTITY_RENAME = {
    "SS_ID": "ss_id",
    "SS_NAME": "ss_name",
    "SS_OPERATOR": "ss_operator",
    "SS_VOLTAGE": "ss_voltage",
    "SS_TYPE": "ss_type",
    "REGION": "region",
    "REGION_ID": "region_id",
}

# Source parquet uses 'earthquake'; schema uses 'seismic' (IM convention).
EDR_HAZARD_RENAME = {
    "im_earthquake": "im_seismic",
    "edr_earthquake": "edr_seismic",
    "eal_earthquake": "eal_seismic",
    "ead_earthquake": "ead_seismic",
}

HAZARD_IM_COLS = {
    "flood": ["flood_depth_m"],
    "seismic": ["pga_475"],
    "landslide": ["ls_n10", "ls_lw", "ls_susc"],
    "wildfire": ["whp_cnt", "whp_cls"],
    "lightning": ["ltng_rate"],
    "wind": ["pe_1pct_maxwind_ms", "pe_2pct_maxwind_ms", "pe_5pct_maxwind_ms"],
    "hail": ["hail_rate", "hail_maxmag"],
    "tornado": [
        "total_hits", "ef2plus_hits", "max_mag",
        "annual_hit_rate", "annual_ef2plus_rate",
    ],
    "fzg": ["R_50RP", "G_50RP", "SPI_50RP", "STUSPS"],
}

TORNADO_RENAME = {"max_mag": "tornado_max_mag"}
FZG_RENAME = {
    "R_50RP": "fzg_r_50rp",
    "G_50RP": "fzg_g_50rp",
    "SPI_50RP": "fzg_spi_50rp",
    "STUSPS": "fzg_stusps",
}

INT_COLS = ("whp_cls", "total_hits", "ef2plus_hits", "tornado_max_mag",
            "max_voltage_kv", "region_id")


def _parse_max_voltage_kv(value: object) -> int | None:
    """Parse 'V1;V2:...' (volts, mixed delimiters) and return max as integer kV."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    import re
    parts = re.split(r"[;:]", str(value))
    volts = [int(p) for p in parts if p.strip().isdigit()]
    if not volts:
        return None
    return max(volts) // 1000


def _load_network() -> gpd.GeoDataFrame:
    gdf = gpd.read_parquet(SUBS_NETWORK)
    if len(gdf) != EXPECTED_NETWORK_ROWS:
        raise ValueError(
            f"network/subs row count {len(gdf)} != expected {EXPECTED_NETWORK_ROWS}"
        )
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        raise ValueError(f"network/subs CRS must be EPSG:4326, got {gdf.crs}")
    required = {"SS_ID", "SS_NAME", "SS_OPERATOR", "SS_VOLTAGE", "SS_TYPE",
                "REGION", "REGION_ID", "connected_tl_id", "geometry"}
    missing = required - set(gdf.columns)
    if missing:
        raise KeyError(f"network/subs missing columns: {missing}")
    return gdf


def _load_cost() -> pd.DataFrame:
    df = pd.read_parquet(SUBS_COST)
    required = {"SS_ID", "replacement_cost_usd", "asset_class",
                "max_line_volt_kv", "volt_snap"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"subs_cost missing columns: {missing}")
    return df[list(required)].copy()


def _load_edr() -> pd.DataFrame:
    df = pd.read_parquet(SUBS_EDR)
    if len(df) != EXPECTED_EDR_ROWS:
        raise ValueError(
            f"subs_edr row count {len(df)} != expected {EXPECTED_EDR_ROWS}"
        )
    df = df.rename(columns=EDR_HAZARD_RENAME)

    hazards_full = ["flood", "seismic", "landslide", "wildfire", "lightning",
                    "wind", "hail", "tornado", "fzg"]
    keep = ["SS_ID"]
    for h in hazards_full:
        keep += [f"im_{h}", f"edr_{h}", f"eal_{h}", f"ead_{h}"]
    keep += ["ead_geomag"]  # only ead_geomag exists in subs_edr; edr/eal/im_geomag are absent

    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise KeyError(f"subs_edr missing columns after rename: {missing}")
    return df[keep].copy()


def _load_geomag_scenario_ead(path, col_name: str) -> pd.DataFrame:
    """Return SS_ID → col_name (mean_failure_prob × replacement_cost_usd)."""
    df = pd.read_parquet(path)[["SS_ID", "mean_failure_prob"]].copy()
    cost = pd.read_parquet(SUBS_COST)[["SS_ID", "replacement_cost_usd"]]
    df = df.merge(cost, on="SS_ID", how="left")
    df[col_name] = df["mean_failure_prob"] * df["replacement_cost_usd"].fillna(0)
    return df[["SS_ID", col_name]]


def _load_hazard_im(hazard: str) -> pd.DataFrame:
    path = SUBS_HAZARD_FILES[hazard]
    df = pd.read_parquet(path)
    cols = HAZARD_IM_COLS[hazard]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"{path.name} missing columns: {missing}")
    out = df[["SS_ID", *cols]].copy()
    if hazard == "tornado":
        out = out.rename(columns=TORNADO_RENAME)
    if hazard == "fzg":
        out = out.rename(columns=FZG_RENAME)
    return out


def build_substations_frame() -> gpd.GeoDataFrame:
    network = _load_network()
    cost = _load_cost()
    edr = _load_edr()

    gdf = network.merge(cost, on="SS_ID", how="left", validate="one_to_one")
    gdf = gdf.merge(edr, on="SS_ID", how="left", validate="one_to_one")

    for hazard in HAZARD_IM_COLS:
        im = _load_hazard_im(hazard)
        gdf = gdf.merge(im, on="SS_ID", how="left", validate="one_to_one")

    # Geomag scenario EAD: mean_failure_prob × replacement_cost for 100yr and 250yr events.
    for path, col in [(SUBS_GEOMAG_100, "ead_geomag_100"), (SUBS_GEOMAG_250, "ead_geomag_250")]:
        scenario = _load_geomag_scenario_ead(path, col)
        gdf = gdf.merge(scenario, on="SS_ID", how="left")

    gdf = gdf.rename(columns=IDENTITY_RENAME)
    gdf["max_voltage_kv"] = gdf["ss_voltage"].apply(_parse_max_voltage_kv)
    gdf["connected_tl_id"] = gdf["connected_tl_id"].apply(
        lambda v: "{" + ",".join(f'"{x}"' for x in v) + "}" if v is not None else None
    )

    gdf = gdf.rename(columns={"geometry": "geom"}).set_geometry("geom")
    if "lat" not in gdf.columns or "lon" not in gdf.columns:
        gdf["lon"] = gdf.geometry.x
        gdf["lat"] = gdf.geometry.y

    for col in INT_COLS:
        if col in gdf.columns:
            gdf[col] = gdf[col].astype("Int64")

    model_cols = set(Substation.__table__.columns.keys())
    keep = [c for c in gdf.columns if c in model_cols]
    gdf = gdf[keep + ["geom"]].copy() if "geom" not in keep else gdf[keep].copy()
    gdf = gdf.set_geometry("geom")

    if len(gdf) != EXPECTED_NETWORK_ROWS:
        raise ValueError(
            f"post-join row count {len(gdf)} != {EXPECTED_NETWORK_ROWS}; "
            "joins must be one-to-one"
        )
    return gdf


def seed() -> int:
    assert_inputs_present()
    gdf = build_substations_frame()

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE substations"))
        gdf.to_postgis(
            "substations",
            con=conn,
            if_exists="append",
            index=False,
            chunksize=2000,
        )
        n = conn.execute(text("SELECT COUNT(*) FROM substations")).scalar_one()

    if n != EXPECTED_NETWORK_ROWS:
        raise RuntimeError(f"post-insert row count {n} != {EXPECTED_NETWORK_ROWS}")
    return n