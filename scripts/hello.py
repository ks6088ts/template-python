import logging
from enum import Enum

import typer


class ModeType(str, Enum):
    one = "one"
    two = "two"


app = typer.Typer(
    name="hello",
    help="A simple command line tool to say hello",
    # add_completion=False,
)
logger = logging.getLogger(__name__)


@app.command(
    help="Say hello to NAME",
)
def hello(
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="The name to say hello to",
    ),
    password: str = typer.Option(
        ...,
        "--password",
        "-p",
        hide_input=True,
        confirmation_prompt=True,
        help="The password to authenticate",
    ),
    mode: ModeType = typer.Option(
        ModeType.one,
        "--mode",
        "-m",
        help="The mode to run",
    ),
    confidence: float = typer.Option(
        0.5,
        "--confidence",
        "-c",
        help="The confidence level",
    ),
    path: str = typer.Option(
        ...,
        "--path",
        envvar="PATH",
        show_envvar=True,
        help="The path to save the output",
    ),
    file: typer.FileText = typer.Option(
        ...,
        "--file",
        "-f",
        help="The file to save the output",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show more information",
    ),
):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.debug("Running in verbose mode")
    typer.echo(f"Hello {name}!")
    typer.echo(f"Your password is: {password}")
    typer.echo(f"Mode: {mode}")
    typer.echo(f"Confidence: {confidence}")
    typer.echo(f"Path: {path}")
    typer.echo(f"File: {file}")
    for line in file.readlines():
        typer.echo(line)
    typer.echo(f"Verbose: {verbose}")


if __name__ == "__main__":
    app()
