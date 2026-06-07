# scripts/build_rasters.py
# Role: CLI orchestrator — builds registered hazard raster overlays
# Author: Dennies Bor

from __future__ import annotations

import sys
from typing import Callable

import typer

from rasters.lightning import build as build_lightning
from rasters.flood_100yr import build as build_flood
from rasters.hail import build as build_hail
from rasters.landslide import build as build_landslide
from rasters.wildfire import build as build_wildfire
from rasters.wind import build as build_wind
from rasters.seismic import build as build_seismic
from rasters.tornado import build as build_tornado
from rasters.geomag import build as build_geomag

app = typer.Typer(no_args_is_help=True, add_completion=False)

# Registry: name -> build function. Add new rasters here.
REGISTRY: dict[str, Callable[[], None]] = {
    "lightning": build_lightning,
    "flood":     build_flood,
    "hail":      build_hail,
    "landslide": build_landslide,
    "wildfire":  build_wildfire,
    "wind":      build_wind,
    "seismic":   build_seismic,
    "tornado":   build_tornado,
    "geomag":    build_geomag,
}


@app.command("all")
def build_all() -> None:
    """Build every registered raster."""
    failed: list[str] = []
    for name, fn in REGISTRY.items():
        typer.echo(f"building {name}…")
        try:
            fn()
            typer.echo(f"  done: {name}")
        except Exception as exc:
            typer.echo(f"  FAILED: {name} — {exc}", err=True)
            failed.append(name)

    if failed:
        typer.echo(f"\n{len(failed)} raster(s) failed: {', '.join(failed)}", err=True)
        raise typer.Exit(1)

    typer.echo(f"\nAll {len(REGISTRY)} rasters built successfully.")


@app.command("one")
def build_one(name: str) -> None:
    """Build a single registered raster by name."""
    if name not in REGISTRY:
        typer.echo(f"unknown raster '{name}'. registered: {', '.join(REGISTRY)}", err=True)
        raise typer.Exit(1)

    typer.echo(f"building {name}…")
    REGISTRY[name]()
    typer.echo(f"done: {name}")


if __name__ == "__main__":
    app()
