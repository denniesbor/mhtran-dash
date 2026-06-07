# api/src/mhtran_api/models/lines.py
# Role: ORM model for HV transmission lines with per-hazard exposure and damage columns
# Author: Dennies Bor

from geoalchemy2 import Geometry
from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from mhtran_api.models.base import Base


class Line(Base):
    __tablename__ = "lines"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    voltage_kv: Mapped[float | None] = mapped_column(Float)
    length_km: Mapped[float | None] = mapped_column(Float)
    volt_snap: Mapped[float | None] = mapped_column(Float, index=True)
    cost_per_km: Mapped[float | None] = mapped_column(Float)
    replacement_cost_usd: Mapped[float | None] = mapped_column(Float)

    geom: Mapped[str] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326, spatial_index=True),
        nullable=False,
    )

    flood_mean: Mapped[float | None] = mapped_column(Float)
    flood_max: Mapped[float | None] = mapped_column(Float)
    flood_p95: Mapped[float | None] = mapped_column(Float)

    im_flood: Mapped[float | None] = mapped_column(Float)
    im_seismic: Mapped[float | None] = mapped_column(Float)
    im_landslide: Mapped[float | None] = mapped_column(Float)
    im_wildfire: Mapped[float | None] = mapped_column(Float)
    im_lightning: Mapped[float | None] = mapped_column(Float)
    im_wind: Mapped[float | None] = mapped_column(Float)
    im_hail: Mapped[float | None] = mapped_column(Float)
    im_tornado: Mapped[float | None] = mapped_column(Float)
    im_fzg: Mapped[float | None] = mapped_column(Float)
    im_geomag: Mapped[float | None] = mapped_column(Float)

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
    eal_geomag: Mapped[float | None] = mapped_column(Float)

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