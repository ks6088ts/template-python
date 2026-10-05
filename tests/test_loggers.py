import logging

import pytest

from template_python.loggers import get_logger


def test_get_logger(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test the get_logger function to ensure it returns a logger instance
    and prints a debug message correctly.
    """
    logger_name = f"{__name__}.configured"
    test_logger = get_logger(logger_name, "DEBUG")
    test_logger.debug(f"{logger_name} logger initialized")
    captured = capsys.readouterr()

    assert test_logger.name == logger_name
    assert f"{logger_name} logger initialized" in captured.err
    assert "DEBUG" in captured.err
    assert "test_loggers.py" in captured.err


def test_get_logger_reconfigures_existing_logger_without_duplicate_handlers() -> None:
    logger_name = f"{__name__}.reconfigured"
    test_logger = get_logger(logger_name, "INFO")
    handlers = tuple(test_logger.handlers)

    reconfigured_logger = get_logger(logger_name, "DEBUG")

    assert reconfigured_logger is test_logger
    assert reconfigured_logger.level == logging.DEBUG
    assert tuple(reconfigured_logger.handlers) == handlers
    assert len(reconfigured_logger.handlers) == 1
    assert reconfigured_logger.propagate is False
