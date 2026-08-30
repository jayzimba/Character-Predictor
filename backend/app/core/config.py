"""Application settings loaded from environment variables.

DATABASE_URL is used from Phase 2. JWT settings are used from Phase 4.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Values come from `.env` or the process environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Personality Classification Using Data Mining"
    app_env: str = "development"
    app_debug: bool = True
    api_prefix: str = "/api"

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    frontend_url: str = "http://127.0.0.1:5173"

    database_url: str = (
        "mysql+pymysql://root@127.0.0.1:3306/personality_classification"
    )

    jwt_secret: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    ml_models_dir: str = "app/ml/models"
    ml_demo_mode: bool = True


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so we do not re-read the file on every request."""
    return Settings()
