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

    # Allowed CORS origins as a comma-separated string (local frontend only by
    # default). Stored as a plain string so dotenv values are not JSON-decoded;
    # use the `cors_origins` property for the parsed list.
    cors_origins_raw: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parsed list of allowed CORS origins."""
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

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

    # --- AI provider selection ---
    # "mock" (default, deterministic, no credentials) or "azure".
    ai_provider: str = Field(default="mock", alias="AI_PROVIDER")

    # --- Azure AI provider (only used when ai_provider == "azure") ---
    # Empty by default; real values come from the environment / Key Vault.
    azure_openai_endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment: str = Field(default="", alias="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = Field(
        default="", alias="AZURE_OPENAI_API_VERSION"
    )
    azure_openai_api_key: str = Field(default="", alias="AZURE_OPENAI_API_KEY")

    # --- Salesforce integration (disabled by default) ---
    salesforce_enabled: bool = Field(default=False, alias="SALESFORCE_ENABLED")
    salesforce_instance_url: str = Field(default="", alias="SALESFORCE_INSTANCE_URL")
    salesforce_client_id: str = Field(default="", alias="SALESFORCE_CLIENT_ID")
    salesforce_client_secret: str = Field(
        default="", alias="SALESFORCE_CLIENT_SECRET"
    )

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
