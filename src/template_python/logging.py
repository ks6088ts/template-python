"""Application logging configuration."""

import logging

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def configure_logging(level: str) -> None:
    """Configure process logging at the application boundary."""
    numeric_level = logging.getLevelNamesMapping().get(level.upper())
    if numeric_level is None:
        msg = f"unsupported log level: {level}"
        raise ValueError(msg)
    logging.basicConfig(level=numeric_level, format=LOG_FORMAT, force=True)
