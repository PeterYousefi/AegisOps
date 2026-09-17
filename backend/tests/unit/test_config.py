"""Unit tests for configuration parsing, especially CORS origins."""

from __future__ import annotations

from app.core.config import Settings


def test_cors_origins_default() -> None:
    settings = Settings(APP_ENV="local")
    assert settings.cors_origins == ["http://localhost:3000"]


def test_cors_origins_parses_comma_separated_string() -> None:
    # This is the shape a dotenv / environment value takes; it must NOT be
    # JSON-decoded (that regression previously crashed startup with a .env file).
    settings = Settings(CORS_ORIGINS="http://localhost:3000, http://localhost:3001")
    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://localhost:3001",
    ]


def test_cors_origins_single_value() -> None:
    settings = Settings(CORS_ORIGINS="https://app.example.com")
    assert settings.cors_origins == ["https://app.example.com"]


def test_log_level_normalized() -> None:
    assert Settings(LOG_LEVEL="debug").log_level == "DEBUG"
    assert Settings(LOG_LEVEL="bogus").log_level == "INFO"
