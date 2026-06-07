# api/src/mhtran_api/routers/health.py
# Role: liveness and readiness endpoints
# Author: Dennies Bor
# Description: /health is liveness; /ready confirms database connectivity.

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from mhtran_api.db import get_session

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadyResponse(BaseModel):
    status: str
    database: str
    postgis_version: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="mhtran-api", version="0.1.0")


@router.get("/ready", response_model=ReadyResponse)
def ready(session: Session = Depends(get_session)) -> ReadyResponse:
    result = session.execute(text("SELECT PostGIS_Full_Version()")).scalar_one()
    return ReadyResponse(status="ok", database="reachable", postgis_version=result)