# api/src/mhtran_api/config.py
# Role: application settings loaded from environment
# Author: Dennies Bor
# Description: pydantic-settings wrapper around env vars; fails fast if
#              required values are missing.

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = Field(..., alias="DATABASE_URL")
    env: str = Field("dev", alias="MHTRAN_ENV")


def get_settings() -> Settings:
    return Settings()