"""Typed application settings."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ProjectSettings(BaseSettings):
    """Settings loaded from ``PROJECT_*`` environment variables."""

    name: str = "template-python"
    log_level: LogLevel = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PROJECT_",
        case_sensitive=False,
        extra="forbid",
    )


def get_project_settings() -> ProjectSettings:
    """Load and validate settings for the current process."""
    return ProjectSettings()
