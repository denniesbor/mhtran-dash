# api/src/mhtran_api/models/substations.py
# Role: ORM model for HV substations with per-hazard exposure and damage columns
# Author: Dennies Bor
# Description: wide schema; one row per substation; hazard columns nullable for
#              substations outside the fragility analysis scope.

from sqlalchemy import Float, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from mhtran_api.models.base import Base


class Substation(Base):
    __tablename__ = "substations"

    ss_id: Mapped[str] = mapped_column(String, primary_key=True)
    ss_name: Mapped[str | None] = mapped_column(String)
    ss_operator: Mapped[str | None] = mapped_column(String)
    ss_voltage: Mapped[str | None] = mapped_column(String)
    max_voltage_kv: Mapped[int | None] = mapped_column(Integer, index=True)
    ss_type: Mapped[str | None] = mapped_column(String)
    region: Mapped[str | None] = mapped_column(String, index=True)
    region_id: Mapped[int | None] = mapped_column(Integer, index=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    connected_tl_id: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    max_line_volt_kv: Mapped[float | None] = mapped_column(Float)
    volt_snap: Mapped[float | None] = mapped_column(Float, index=True)
    asset_class: Mapped[str | None] = mapped_column(String, index=True)
    replacement_cost_usd: Mapped[float | None] = mapped_column(Float)

    geom: Mapped[str] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )

    flood_depth_m: Mapped[float | None] = mapped_column(Float)
    pga_475: Mapped[float | None] = mapped_column(Float)
    ls_n10: Mapped[float | None] = mapped_column(Float)
    ls_lw: Mapped[float | None] = mapped_column(Float)
    ls_susc: Mapped[float | None] = mapped_column(Float)
    whp_cnt: Mapped[float | None] = mapped_column(Float)
    whp_cls: Mapped[int | None] = mapped_column(Integer)
    ltng_rate: Mapped[float | None] = mapped_column(Float)
    pe_1pct_maxwind_ms: Mapped[float | None] = mapped_column(Float)
    pe_2pct_maxwind_ms: Mapped[float | None] = mapped_column(Float)
    pe_5pct_maxwind_ms: Mapped[float | None] = mapped_column(Float)
    hail_rate: Mapped[float | None] = mapped_column(Float)
    hail_maxmag: Mapped[float | None] = mapped_column(Float)
    total_hits: Mapped[int | None] = mapped_column(Integer)
    ef2plus_hits: Mapped[int | None] = mapped_column(Integer)
    tornado_max_mag: Mapped[int | None] = mapped_column(Integer)
    annual_hit_rate: Mapped[float | None] = mapped_column(Float)
    annual_ef2plus_rate: Mapped[float | None] = mapped_column(Float)
    fzg_r_50rp: Mapped[float | None] = mapped_column(Float)
    fzg_g_50rp: Mapped[float | None] = mapped_column(Float)
    fzg_spi_50rp: Mapped[float | None] = mapped_column(Float)
    fzg_stusps: Mapped[str | None] = mapped_column(String)

    im_flood: Mapped[float | None] = mapped_column(Float)
    im_seismic: Mapped[float | None] = mapped_column(Float)
    im_landslide: Mapped[float | None] = mapped_column(Float)
    im_wildfire: Mapped[float | None] = mapped_column(Float)
    im_lightning: Mapped[float | None] = mapped_column(Float)
    im_wind: Mapped[float | None] = mapped_column(Float)
    im_hail: Mapped[float | None] = mapped_column(Float)
    im_tornado: Mapped[float | None] = mapped_column(Float)
    im_fzg: Mapped[float | None] = mapped_column(Float)

    edr_flood: Mapped[float | None] = mapped_column(Float, index=True)
    edr_seismic: Mapped[float | None] = mapped_column(Float, index=True)
    edr_landslide: Mapped[float | None] = mapped_column(Float, index=True)
    edr_wildfire: Mapped[float | None] = mapped_column(Float, index=True)
    edr_lightning: Mapped[float | None] = mapped_column(Float, index=True)
    edr_wind: Mapped[float | None] = mapped_column(Float, index=True)
    edr_hail: Mapped[float | None] = mapped_column(Float, index=True)
    edr_tornado: Mapped[float | None] = mapped_column(Float, index=True)
    edr_fzg: Mapped[float | None] = mapped_column(Float, index=True)
    edr_geomag: Mapped[float | None] = mapped_column(Float, index=True)

    eal_flood: Mapped[float | None] = mapped_column(Float)
    eal_seismic: Mapped[float | None] = mapped_column(Float)
    eal_landslide: Mapped[float | None] = mapped_column(Float)
    eal_wildfire: Mapped[float | None] = mapped_column(Float)
    eal_lightning: Mapped[float | None] = mapped_column(Float)
    eal_wind: Mapped[float | None] = mapped_column(Float)
    eal_hail: Mapped[float | None] = mapped_column(Float)
    eal_tornado: Mapped[float | None] = mapped_column(Float)
    eal_fzg: Mapped[float | None] = mapped_column(Float)

    ead_flood: Mapped[float | None] = mapped_column(Float, index=True)
    ead_seismic: Mapped[float | None] = mapped_column(Float, index=True)
    ead_landslide: Mapped[float | None] = mapped_column(Float, index=True)
    ead_wildfire: Mapped[float | None] = mapped_column(Float, index=True)
    ead_lightning: Mapped[float | None] = mapped_column(Float, index=True)
    ead_wind: Mapped[float | None] = mapped_column(Float, index=True)
    ead_hail: Mapped[float | None] = mapped_column(Float, index=True)
    ead_tornado: Mapped[float | None] = mapped_column(Float, index=True)
    ead_fzg: Mapped[float | None] = mapped_column(Float, index=True)
    ead_geomag: Mapped[float | None] = mapped_column(Float, index=True)
    ead_geomag_100: Mapped[float | None] = mapped_column(Float, index=True)
    ead_geomag_250: Mapped[float | None] = mapped_column(Float, index=True)