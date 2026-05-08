"""Tests for :mod:`template_python.settings`."""

from __future__ import annotations

from pathlib import Path

import pytest
from dotenv import dotenv_values

from template_python.loggers import get_logger
from template_python.settings import Settings, get_project_settings

logger = get_logger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_TEMPLATE = REPO_ROOT / ".env.template"


def test_settings_defaults(
    clean_env: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """When no env vars and no .env file are present, defaults are used."""
    # `chdir` into a clean directory so pydantic-settings cannot pick up a
    # local `.env` file from the developer's workspace.
    clean_env.chdir(tmp_path)
    settings = Settings()
    assert settings.project_name == "default-project"
    assert settings.project_log_level == "INFO"


def test_settings_env_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Environment variables override the defaults without polluting globals."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PROJECT_NAME", "from-env")
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "DEBUG")
    settings = Settings()
    assert settings.project_name == "from-env"
    assert settings.project_log_level == "DEBUG"


def test_settings_invalid_log_level_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An unsupported log level should fail validation."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "INVALID")
    with pytest.raises(ValueError, match="project_log_level"):
        Settings()


def test_settings_loaded_from_template_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The shipped ``.env.template`` file should produce a valid Settings object."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PROJECT_NAME", raising=False)
    monkeypatch.delenv("PROJECT_LOG_LEVEL", raising=False)

    # Inject the template values via the environment instead of relying on the
    # private ``_env_file`` keyword argument, which is not part of the typed
    # public API of pydantic-settings.
    for key, value in dotenv_values(ENV_TEMPLATE).items():
        if value is not None:
            monkeypatch.setenv(key, value)

    settings = Settings()
    assert settings.project_name == "template-python"
    assert settings.project_log_level == "INFO"


def test_get_project_settings_is_cached(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """``get_project_settings`` returns the same instance across calls."""
    monkeypatch.chdir(tmp_path)
    first = get_project_settings()
    second = get_project_settings()
    assert first is second
