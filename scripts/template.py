"""Vanilla Typer CLI skeleton.

This script is intentionally kept as a stand-alone example. It is not
shipped as part of the :mod:`template_python` package; copy and adapt it
when you want to expose your own command-line interface.

Run it with::

    uv run python scripts/template.py hello --name World --verbose
"""

from __future__ import annotations

import logging
from typing import Annotated

import typer
from dotenv import load_dotenv

from template_python.core import hello_world
from template_python.loggers import get_logger
from template_python.settings import get_project_settings

app = typer.Typer(
    add_completion=False,
    help="template-python CLI",
)

logger = get_logger(__name__)


def set_verbose_logging(verbose: bool) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)


@app.command()
def hello(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the person to greet",
        ),
    ] = "World",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
) -> None:
    set_verbose_logging(verbose)

    hello_world(verbose=verbose)
    logger.debug("This is a debug message with name: %s", name)
    logger.info(
        "Settings from .env: %s",
        get_project_settings().model_dump_json(indent=2),
    )


if __name__ == "__main__":
    if not load_dotenv(override=True, verbose=True):
        logger.warning("No .env file found; using defaults")
    app()
