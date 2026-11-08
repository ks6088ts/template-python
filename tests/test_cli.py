import json
import runpy
import sys
from pathlib import Path

import pytest
from pydantic import SecretStr
from typer.testing import CliRunner

from template_python import __version__, cli
from template_python.cli import app
from template_python.settings import ProjectSettings

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "A minimal, typed Python project template." in result.stdout


def test_cli_without_command_shows_help() -> None:
    result = runner.invoke(app, [])

    assert result.exit_code == 2
    assert "Usage:" in result.stdout


@pytest.mark.parametrize("flag", ["--version", "-V"])
def test_cli_version(flag: str) -> None:
    result = runner.invoke(app, [flag])

    assert result.exit_code == 0
    assert result.stdout == f"template-python {__version__}\n"


def test_cli_version_ignores_invalid_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "VERBOSE")

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0


def test_cli_greets_name() -> None:
    result = runner.invoke(app, ["hello", "--name", "Ada"])

    assert result.exit_code == 0
    assert result.stdout == "Hello, Ada!\n"


def test_cli_verbose_logging() -> None:
    result = runner.invoke(app, ["--verbose", "hello"])

    assert result.exit_code == 0
    assert "Loaded settings for template-python" in result.stderr
    assert result.stdout == "Hello, World!\n"


def test_cli_json_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_LOG_FORMAT", "json")

    result = runner.invoke(app, ["--verbose", "hello"])

    assert result.exit_code == 0
    record = json.loads(result.stderr.splitlines()[0])
    assert record["level"] == "DEBUG"
    assert record["message"] == "Loaded settings for template-python"


def test_cli_rejects_blank_name() -> None:
    result = runner.invoke(app, ["hello", "--name", " "])

    assert result.exit_code == 2
    assert "name must not be blank" in result.stderr


def test_cli_reports_invalid_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "VERBOSE")

    result = runner.invoke(app, ["hello"])

    assert result.exit_code == 2
    assert "Invalid configuration" in result.stderr


def test_cli_reads_dotenv_from_working_directory(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("PROJECT_NAME=from-dotenv\n", encoding="utf-8")

    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert json.loads(result.stdout)["name"] == "from-dotenv"


def test_cli_config_shows_effective_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_LOG_FORMAT", "json")

    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"name": "template-python", "log_level": "INFO", "log_format": "json"}


def test_cli_config_masks_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    class SettingsWithSecret(ProjectSettings):
        api_key: SecretStr = SecretStr("do-not-print")

    monkeypatch.setattr(cli, "get_project_settings", SettingsWithSecret)

    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert "do-not-print" not in result.stdout
    assert json.loads(result.stdout)["api_key"] == "**********"


def test_module_entry_point(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["template_python", "hello", "--name", "Module"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("template_python", run_name="__main__")

    assert exc_info.value.code == 0
    assert capsys.readouterr().out == "Hello, Module!\n"
