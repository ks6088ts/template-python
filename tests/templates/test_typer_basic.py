from typer.testing import CliRunner

from templates.typer_basic import app

runner = CliRunner()


def test_app():
    args = [
        ["--help"],
        ["--name", "name", "--password", "password", "--file", "./README.md", "--verbose"],
    ]
    for arg in args:
        result = runner.invoke(app=app, args=arg)
        assert result.exit_code == 0
