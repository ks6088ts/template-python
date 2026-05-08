"""Tests for :mod:`template_python.loggers`."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from template_python.loggers import get_logger

if TYPE_CHECKING:
    import pytest


def test_get_logger_emits_records(caplog: pytest.LogCaptureFixture) -> None:
    """The returned logger should emit records that pytest can capture."""
    name = "template_python.tests.test_loggers"
    with caplog.at_level(logging.DEBUG, logger=name):
        test_logger = get_logger(name, log_level=logging.DEBUG)
        test_logger.debug("logger initialized")

    assert test_logger.name == name
    assert "logger initialized" in caplog.text


def test_get_logger_is_idempotent() -> None:
    """Calling :func:`get_logger` twice must not duplicate handlers."""
    name = "template_python.tests.test_loggers.idempotent"
    first = get_logger(name)
    second = get_logger(name)
    assert first is second
    assert len(first.handlers) == 1


def test_get_logger_respects_explicit_level() -> None:
    """An explicit ``log_level`` argument overrides the project setting."""
    name = "template_python.tests.test_loggers.level"
    test_logger = get_logger(name, log_level=logging.WARNING)
    assert test_logger.level == logging.WARNING
