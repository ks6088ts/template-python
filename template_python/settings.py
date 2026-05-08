"""Project settings loaded from environment variables and `.env` files."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]


class Settings(BaseSettings):
    """Application settings.

    Values are loaded with the following precedence (highest first):

    1. Environment variables.
    2. Variables defined in a local `.env` file.
    3. Defaults declared on the model.
    """

    project_name: str = "default-project"
    project_log_level: LogLevel = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_project_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
