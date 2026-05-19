"""
Application configuration.

All settings are read from environment variables (or a .env file).
Pydantic-Settings validates types and provides sensible defaults so the
server can start in development without a full .env file.
"""

from __future__ import annotations

import json
import os
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── MongoDB ────────────────────────────────────────────────────────────
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL",
    )
    # Central database – users, plans, quotas, audit logs (core accesses this only)
    CENTRAL_DB_NAME: str = Field(
        default="mindsqubit_core",
        description="Name of the central (platform) database",
    )

    # ── JWT ────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(
        default="",
        description="Secret key for JWT signing (required in production)",
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # ── OAuth ──────────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GITHUB_CLIENT_ID: str = Field(default="")
    GITHUB_CLIENT_SECRET: str = Field(default="")

    # ── CORS & redirects ───────────────────────────────────────────────────
    CORS_ORIGINS: Union[str, List[str]] = Field(default="http://localhost:3000")
    OAUTH_REDIRECT_URL: str = Field(
        default="http://localhost:8000/api/v1/auth/oauth"
    )

    # ── Agent microservices ───────────────────────────────────────────────
    AGENT_SERVICE_API_KEY: str = Field(
        default="",
        description="Shared secret between core and agent services",
    )
    AGENT_GATEWAY_TIMEOUT_SECONDS: float = Field(default=60.0)

    AGENT_CODECRAFT_URL: str = Field(default="http://localhost:8010")
    AGENT_DATAVIZ_URL: str = Field(default="http://localhost:8011")
    AGENT_CONTENTCREATOR_URL: str = Field(default="http://localhost:8012")
    AGENT_DESIGNMASTER_URL: str = Field(default="http://localhost:8013")
    AGENT_LANGUAGETUTOR_URL: str = Field(default="http://localhost:8014")
    AGENT_RESEARCHPRO_URL: str = Field(default="http://localhost:8015")
    AGENT_TECHBLOG_URL: str = Field(default="http://localhost:8016")
    AGENT_OPPORTUNITYALERT_URL: str = Field(default="http://localhost:8017")

    # ── Plans ──────────────────────────────────────────────────────────────
    DEFAULT_PLAN_ID: str = Field(
        default="free",
        description="Plan assigned to every new user",
    )

    # ── Server ─────────────────────────────────────────────────────────────
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # ── Validators ─────────────────────────────────────────────────────────
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        if v is None:
            return ["http://localhost:3000"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
            origins = [o.strip() for o in v.split(",") if o.strip()]
            return origins or ["http://localhost:3000"]
        return ["http://localhost:3000"]

    # ── Convenience properties ─────────────────────────────────────────────
    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [self.CORS_ORIGINS] if self.CORS_ORIGINS else ["http://localhost:3000"]


settings = Settings()
