# api/src/mhtran_api/main.py
# Role: FastAPI application entrypoint
# Author: Dennies Bor
# Description: builds the app, mounts routers, exposes /health for liveness.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mhtran_api.routers import health, map


def create_app() -> FastAPI:
    app = FastAPI(
        title="mhtran-dash API",
        version="0.1.0",
        description="Multi-hazard transmission dashboard backend.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://mhtran.denniesbor.com",
            "https://mhtran.denniesbor.me",
            "https://denniesbor.github.io",
            "http://localhost:5173",
        ],
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(map.router)
    return app


app = create_app()