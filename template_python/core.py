"""Core domain logic for template-python."""

from __future__ import annotations

import logging

from template_python.loggers import get_logger

logger = get_logger(__name__)


def hello_world(verbose: bool = False) -> None:
    """Log a greeting message.

    Args:
        verbose: If ``True``, the message is logged at ``DEBUG`` level.
            Otherwise it is logged at ``INFO`` level.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logger.log(level, "Hello World")


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    hello_world(verbose=True)
