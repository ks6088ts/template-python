"""Typer command-line application."""

import logging
from typing import Annotated

import typer
from pydantic import ValidationError

from template_python.core import greeting
from template_python.logging import configure_logging
from template_python.settings import get_project_settings

app = typer.Typer(
    add_completion=False,
    help="A minimal, typed Python project template.",
    no_args_is_help=True,
)
logger = logging.getLogger(__name__)


@app.callback()
def main(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable debug logging."),
    ] = False,
) -> None:
    """Configure the application before running a command."""
    try:
        settings = get_project_settings()
    except ValidationError as exc:
        typer.echo(f"Invalid configuration: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    configure_logging("DEBUG" if verbose else settings.log_level)
    logger.debug("Loaded settings for %s", settings.name)


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
