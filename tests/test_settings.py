import pytest
from pydantic import ValidationError

from template_python.settings import ProjectSettings


def test_settings_use_prefixed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_NAME", "example")
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "DEBUG")

    settings = ProjectSettings(_env_file=None)

    assert settings.name == "example"
    assert settings.log_level == "DEBUG"


def test_settings_reject_invalid_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "VERBOSE")

    with pytest.raises(ValidationError):
        ProjectSettings(_env_file=None)
