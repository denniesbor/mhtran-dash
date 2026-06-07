# api/src/mhtran_api/seeds/lines.py
# Role: seed the lines table from research parquet outputs
# Author: Dennies Bor
# Description: joins network/lines with lines_cost, lines_edr, and lines_flood;
#              writes via GeoPandas to_postgis with truncate-and-append semantics.

import geopandas as gpd
import pandas as pd
from sqlalchemy import Integer as SaInteger, text

from mhtran_api.db import engine
from mhtran_api.models.lines import Line
from mhtran_api.seeds.paths import (
    LINES_COST,
    LINES_EDR,
    LINES_FLOOD,
    LINES_NETWORK,
    assert_lines_inputs_present,
)

EXPECTED_NETWORK_ROWS = 13908
EXPECTED_EDR_ROWS = 6114

# parquet uses 'earthquake'; DB schema uses 'seismic'
EDR_HAZARD_RENAME = {
    "im_earthquake": "im_seismic",
    "edr_earthquake": "edr_seismic",
    "eal_earthquake": "eal_seismic",
    "ead_earthquake": "ead_seismic",
}


def _load_network() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(LINES_NETWORK) if str(LINES_NETWORK).endswith(".gpkg") \
        else gpd.read_parquet(LINES_NETWORK)
    if len(gdf) != EXPECTED_NETWORK_ROWS:
        raise ValueError(
            f"network/lines row count {len(gdf)} != expected {EXPECTED_NETWORK_ROWS}"
        )
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        raise ValueError(f"network/lines CRS must be EPSG:4326, got {gdf.crs}")
    required = {"name", "V", "length", "geometry"}
    missing = required - set(gdf.columns)
    if missing:
        raise KeyError(f"network/lines missing columns: {missing}")
    return gdf.rename(columns={"V": "voltage_kv", "length": "length_km"})


def _load_cost() -> pd.DataFrame:
    df = pd.read_parquet(LINES_COST)
    required = {"name", "volt_snap", "cost_per_km", "replacement_cost_usd"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"lines_cost missing columns: {missing}")
    return df[list(required)].copy()


def _load_edr() -> pd.DataFrame:
    df = pd.read_parquet(LINES_EDR)
    if len(df) != EXPECTED_EDR_ROWS:
        raise ValueError(
            f"lines_edr row count {len(df)} != expected {EXPECTED_EDR_ROWS}"
        )
    df = df.rename(columns=EDR_HAZARD_RENAME)
    hazards = ["flood", "seismic", "landslide", "wildfire", "lightning",
               "wind", "hail", "tornado", "fzg"]
    keep = ["name"]
    for h in hazards:
        keep += [f"im_{h}", f"edr_{h}", f"eal_{h}", f"ead_{h}"]
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise KeyError(f"lines_edr missing columns after rename: {missing}")
    return df[keep].copy()


def _load_flood() -> pd.DataFrame:
    df = pd.read_parquet(LINES_FLOOD)
    required = {"name", "flood_mean", "flood_max", "flood_p95"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"lines_flood missing columns: {missing}")
    return df[list(required)].copy()


def build_lines_frame() -> gpd.GeoDataFrame:
    network = _load_network()
    cost = _load_cost()
    edr = _load_edr()
    flood = _load_flood()

    gdf = network.merge(cost, on="name", how="left", validate="one_to_one")
    gdf = gdf.merge(edr, on="name", how="left", validate="one_to_one")
    gdf = gdf.merge(flood, on="name", how="left", validate="one_to_one")

    gdf = gdf.rename(columns={"geometry": "geom"}).set_geometry("geom")

    int_cols = [
        col.name for col in Line.__table__.columns
        if isinstance(col.type, SaInteger) and col.name in gdf.columns
    ]
    for col in int_cols:
        gdf[col] = gdf[col].astype("Int64")

    model_cols = set(Line.__table__.columns.keys())
    keep = [c for c in gdf.columns if c in model_cols]
    gdf = gdf[keep].copy()
    gdf = gdf.set_geometry("geom")

    if len(gdf) != EXPECTED_NETWORK_ROWS:
        raise ValueError(
            f"post-join row count {len(gdf)} != {EXPECTED_NETWORK_ROWS}; "
            "joins must be one-to-one"
        )
    return gdf


def seed() -> int:
    assert_lines_inputs_present()
    gdf = build_lines_frame()

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE lines"))
        gdf.to_postgis(
            "lines",
            con=conn,
            if_exists="append",
            index=False,
            chunksize=1000,
        )
        n = conn.execute(text("SELECT COUNT(*) FROM lines")).scalar_one()

    if n != EXPECTED_NETWORK_ROWS:
        raise RuntimeError(f"post-insert row count {n} != {EXPECTED_NETWORK_ROWS}")
    return n
