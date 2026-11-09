from pathlib import Path

import pytest
from pydantic import ValidationError

from template_python.settings import ProjectSettings


def test_settings_defaults() -> None:
    settings = ProjectSettings(_env_file=None)

    assert settings.name == "template-python"
    assert settings.log_level == "INFO"
    assert settings.log_format == "text"


def test_settings_use_prefixed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_NAME", "example")
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("PROJECT_LOG_FORMAT", "json")

    settings = ProjectSettings(_env_file=None)

    assert settings.name == "example"
    assert settings.log_level == "DEBUG"
    assert settings.log_format == "json"


def test_environment_overrides_dotenv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".env").write_text("PROJECT_NAME=from-file\nPROJECT_LOG_LEVEL=ERROR\n", encoding="utf-8")
    monkeypatch.setenv("PROJECT_NAME", "from-env")

    settings = ProjectSettings()

    assert settings.name == "from-env"
    assert settings.log_level == "ERROR"


def test_settings_reject_unknown_dotenv_entry(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("PROJECT_UNKNOWN=1\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        ProjectSettings()


@pytest.mark.parametrize(("variable", "value"), [("PROJECT_LOG_LEVEL", "VERBOSE"), ("PROJECT_LOG_FORMAT", "xml")])
def test_settings_reject_invalid_values(monkeypatch: pytest.MonkeyPatch, variable: str, value: str) -> None:
    monkeypatch.setenv(variable, value)

    with pytest.raises(ValidationError):
        ProjectSettings(_env_file=None)
