# api/src/mhtran_api/main.py
# Role: FastAPI application entrypoint
# Author: Dennies Bor
# Description: builds the app, mounts routers, exposes /health for liveness.

from fastapi import FastAPI

from mhtran_api.routers import health, map


def create_app() -> FastAPI:
    app = FastAPI(
        title="mhtran-dash API",
        version="0.1.0",
        description="Multi-hazard transmission dashboard backend.",
    )
    app.include_router(health.router)
    app.include_router(map.router)
    return app


app = create_app()