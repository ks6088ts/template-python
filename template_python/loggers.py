"""Logging helpers used across the project."""

from __future__ import annotations

import logging

from template_python.settings import get_project_settings

_LOG_FORMAT = "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"


def get_logger(
    name: str = "default",
    log_level: str | int | None = None,
) -> logging.Logger:
    """Return a configured logger.

    If the logger already has handlers, it is returned as-is to avoid adding
    duplicate handlers on repeated calls.

    Args:
        name: The name of the logger.
        log_level: The logging level. Defaults to the project setting.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    if log_level is None:
        log_level = get_project_settings().project_log_level

    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logger.addHandler(handler)
    return logger
