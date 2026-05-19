from __future__ import annotations

import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    AGENT_ID: str
    AGENT_SERVICE_API_KEY: str = ""
    MONGODB_URL: str = "mongodb://localhost:27017"
    AGENT_DB_PREFIX: str = "mindsqubit_agent_"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    HOST: str = "0.0.0.0"
    PORT: int = 8010

    @property
    def db_name(self) -> str:
        return f"{self.AGENT_DB_PREFIX}{self.AGENT_ID}"
