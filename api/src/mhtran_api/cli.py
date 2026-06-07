# api/src/mhtran_api/cli.py
# Role: command-line entrypoint for admin tasks
# Author: Dennies Bor
# Description: typer app exposing seed subcommands.

import typer

from mhtran_api.seeds import lines as seed_lines
from mhtran_api.seeds import substations as seed_substations

app = typer.Typer(no_args_is_help=True, add_completion=False)
seed_app = typer.Typer(no_args_is_help=True, help="Seed database tables from research parquets.")
app.add_typer(seed_app, name="seed")


@seed_app.command("substations")
def seed_substations_cmd() -> None:
    """Seed substations table from network/subs + subs_edr + per-hazard files."""
    n = seed_substations.seed()
    typer.echo(f"seeded substations: {n} rows")


@seed_app.command("lines")
def seed_lines_cmd() -> None:
    """Seed lines table from network/lines + lines_edr + lines_cost + lines_flood."""
    n = seed_lines.seed()
    typer.echo(f"seeded lines: {n} rows")


if __name__ == "__main__":
    app()