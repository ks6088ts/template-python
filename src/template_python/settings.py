"""Typed application settings."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogFormat = Literal["text", "json"]


class ProjectSettings(BaseSettings):
    """Settings loaded from ``PROJECT_*`` environment variables and an optional ``.env`` file.

    Declare credentials as ``pydantic.SecretStr`` so they are masked in ``repr`` and in
    the ``config`` command output.
    """

    name: str = "template-python"
    log_level: LogLevel = "INFO"
    log_format: LogFormat = "text"

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
