"""Application configuration.

Typed, validated settings sourced from environment variables with safe
local-development defaults. This module intentionally does NOT load or require
Azure, Salesforce, PostgreSQL, or AI-provider credentials — those belong to
later tasks and their own settings.

Nothing here logs configuration values, to avoid leaking anything that may
later become sensitive.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the AegisOps backend.

    Values are read from environment variables (and an optional local `.env`
    file). All fields have safe local defaults so the app runs with no
    external configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ignore unrelated env vars (e.g. future providers)
    )

    # Fixed service identity (not secret, not environment-derived).
    service_name: str = "aegisops-api"

    # Deployment environment label, e.g. "local", "dev", "prod".
    app_env: str = Field(default="local", alias="APP_ENV")

    # Logging level name, e.g. "DEBUG", "INFO", "WARNING".
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Prefix under which versioned API routes are mounted.
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    # Allowed CORS origins. Defaults to the local frontend origin only.
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        alias="CORS_ORIGINS",
    )

    # --- Database connection parts (assembled into a URL in shared.db) ---
    # Safe local defaults. Credentials are never hard-coded; production values
    # come from the environment / Key Vault. Never logged.
    postgres_user: str = Field(default="aegisops", alias="POSTGRES_USER")
    # Non-secret local-development default only; real values come from the
    # environment / Key Vault and are never committed.
    postgres_password: str = Field(default="local-dev-only", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="aegisops", alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        """Allow CORS_ORIGINS to be a comma-separated string in the env.

        Accepts either a real list (from code/tests) or a comma-separated
        string (from an environment variable), e.g.
        "http://localhost:3000,http://localhost:3001".
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("log_level")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        """Normalize the log level to an uppercase, known name."""
        normalized = value.strip().upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in allowed:
            return "INFO"
        return normalized


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Cached so the environment is parsed once per process. Tests can clear the
    cache via ``get_settings.cache_clear()`` when they override environment
    variables.
    """
    return Settings()
