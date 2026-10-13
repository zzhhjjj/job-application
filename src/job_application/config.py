"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration.

    Environment variables use the ``JOB_APPLICATION_`` prefix. For example,
    ``JOB_APPLICATION_DATABASE_URL`` overrides ``database_url``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="JOB_APPLICATION_",
        extra="ignore",
    )

    database_url: str = "sqlite:///./jobs.db"
    http_timeout_seconds: float = Field(default=20.0, gt=0)
    http_user_agent: str = "job-application/0.1 (+personal-job-tracker)"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance for the current process."""

    return Settings()
