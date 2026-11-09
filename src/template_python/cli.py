"""Typer command-line application."""

import logging
from typing import Annotated

import typer
from pydantic import ValidationError

from template_python import __version__
from template_python.core import greeting
from template_python.log import configure_logging
from template_python.settings import ProjectSettings, get_project_settings

app = typer.Typer(
    add_completion=False,
    help="A minimal, typed Python project template.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)
logger = logging.getLogger(__name__)


def _print_version(value: bool) -> None:
    if value:
        typer.echo(f"template-python {__version__}")
        raise typer.Exit


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable debug logging."),
    ] = False,
    _version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=_print_version,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Load settings and configure logging before running a command."""
    try:
        settings = get_project_settings()
    except ValidationError as exc:
        typer.echo(f"Invalid configuration: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    configure_logging("DEBUG" if verbose else settings.log_level, settings.log_format)
    logger.debug("Loaded settings for %s", settings.name)
    ctx.obj = settings


@app.command()
def hello(
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Name of the person to greet."),
    ] = "World",
) -> None:
    """Print a greeting."""
    try:
        message = greeting(name)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--name") from exc
    typer.echo(message)


@app.command("config")
def show_config(ctx: typer.Context) -> None:
    """Print the effective configuration as JSON; secret values are masked."""
    settings = ctx.ensure_object(ProjectSettings)
    typer.echo(settings.model_dump_json(indent=2))
