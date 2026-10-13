import pytest
from typer.testing import CliRunner

from template_python.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "A minimal, typed Python project template." in result.stdout


def test_cli_greets_name() -> None:
    result = runner.invoke(app, ["hello", "--name", "Ada"])

    assert result.exit_code == 0
    assert result.stdout == "Hello, Ada!\n"


def test_cli_verbose_logging() -> None:
    result = runner.invoke(app, ["--verbose", "hello"])

    assert result.exit_code == 0
    assert "Loaded settings for template-python" in result.stderr


def test_cli_rejects_blank_name() -> None:
    result = runner.invoke(app, ["hello", "--name", " "])

    assert result.exit_code == 2
    assert "name must not be blank" in result.stderr


def test_cli_reports_invalid_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_LOG_LEVEL", "VERBOSE")

    result = runner.invoke(app, ["hello"])

    assert result.exit_code == 2
    assert "Invalid configuration" in result.stderr
