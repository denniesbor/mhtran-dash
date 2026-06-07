# api/src/mhtran_api/routers/map.py
# Role: GeoJSON endpoints for the map layers
# Author: Dennies Bor

import geopandas as gpd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import text

from mhtran_api.db import engine

router = APIRouter(prefix="/api", tags=["map"])

SUBS_HAZARDS = frozenset([
    "flood", "seismic", "landslide", "wildfire", "lightning",
    "wind", "hail", "tornado", "fzg", "geomag",
])
LINES_HAZARDS = SUBS_HAZARDS - {"geomag"}

SUBS_IDENTITY = [
    "ss_id", "ss_name", "ss_operator", "region",
    "asset_class", "max_voltage_kv", "replacement_cost_usd",
]
LINES_IDENTITY = [
    "name", "voltage_kv", "length_km", "volt_snap", "replacement_cost_usd",
]

SUBS_EAD_COLS = [f"ead_{h}" for h in sorted(SUBS_HAZARDS)] + ["ead_geomag_100", "ead_geomag_250"]
LINES_EAD_COLS = [f"ead_{h}" for h in sorted(LINES_HAZARDS)]

MAX_SIMPLIFY_TOLERANCE = 0.5  # degrees, ~55 km — anything beyond is meaningless

_CACHE = "public, max-age=3600"


def _geojson_response(gdf: gpd.GeoDataFrame) -> Response:
    return Response(
        content=gdf.to_json(),
        media_type="application/geo+json",
        headers={"Cache-Control": _CACHE},
    )


@router.get("/substations")
def get_substations(
    hazard: str | None = Query(default=None, description="Filter to features with non-null EAD for this hazard"),
) -> Response:
    if hazard is not None and hazard not in SUBS_HAZARDS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown hazard '{hazard}'. Valid: {sorted(SUBS_HAZARDS)}",
        )

    cols = ", ".join(SUBS_IDENTITY + SUBS_EAD_COLS + ["geom"])
    if hazard == "geomag":
        where = "WHERE ead_geomag_100 IS NOT NULL OR ead_geomag IS NOT NULL"
    elif hazard:
        where = f"WHERE ead_{hazard} IS NOT NULL"
    else:
        where = ""
    sql = text(f"SELECT {cols} FROM substations {where}")

    gdf = gpd.read_postgis(sql, engine, geom_col="geom")
    return _geojson_response(gdf)


@router.get("/lines")
def get_lines(
    hazard: str | None = Query(default=None, description="Filter to features with non-null EAD for this hazard"),
    simplify: float | None = Query(
        default=None,
        ge=0.0,
        le=MAX_SIMPLIFY_TOLERANCE,
        description="Geometry simplification tolerance in degrees (~0.01 = ~1 km). Omit for full resolution.",
    ),
) -> Response:
    if hazard is not None and hazard not in LINES_HAZARDS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown hazard '{hazard}'. Valid: {sorted(LINES_HAZARDS)}",
        )

    non_geom_cols = ", ".join(LINES_IDENTITY + LINES_EAD_COLS)
    if simplify is not None:
        geom_expr = f"ST_SimplifyPreserveTopology(geom, {simplify}) AS geom"
    else:
        geom_expr = "geom"

    where = f"WHERE ead_{hazard} IS NOT NULL" if hazard else ""
    sql = text(f"SELECT {non_geom_cols}, {geom_expr} FROM lines {where}")

    gdf = gpd.read_postgis(sql, engine, geom_col="geom")
    return _geojson_response(gdf)