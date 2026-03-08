from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Union
import json
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # MongoDB
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URL")
    DATABASE_NAME: str = Field(default="mq_users", description="Database name")

    # JWT
    JWT_SECRET_KEY: str = Field(default="", description="Secret key for JWT signing (required in production)")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry in minutes")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry in days")

    # Gemini
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash", description="Gemini model name (e.g. gemini-1.5-flash, gemini-1.5-pro)")

    # OAuth
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth client secret")
    GITHUB_CLIENT_ID: str = Field(default="", description="GitHub OAuth client ID")
    GITHUB_CLIENT_SECRET: str = Field(default="", description="GitHub OAuth client secret")

    # CORS & OAuth redirects
    CORS_ORIGINS: Union[str, List[str]] = Field(default="http://localhost:3000", description="Comma-separated CORS origins or JSON array")
    OAUTH_REDIRECT_URL: str = Field(default="http://localhost:8000/api/v1/auth/oauth", description="OAuth callback base URL")

    # Server (for uvicorn)
    HOST: str = Field(default="0.0.0.0", description="Server bind host")
    PORT: int = Field(default=8000, description="Server bind port")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
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
            return origins if origins else ["http://localhost:3000"]
        return ["http://localhost:3000"]

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [self.CORS_ORIGINS] if self.CORS_ORIGINS else ["http://localhost:3000"]


settings = Settings()
