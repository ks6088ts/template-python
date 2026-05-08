"""Tests for :mod:`template_python.core`."""

from __future__ import annotations

import logging

import pytest

from template_python.core import hello_world


def test_hello_world_verbose(caplog: pytest.LogCaptureFixture) -> None:
    """The verbose mode logs at ``DEBUG`` level."""
    with caplog.at_level(logging.DEBUG, logger="template_python.core"):
        hello_world(verbose=True)
    assert any(r.levelno == logging.DEBUG and r.message == "Hello World" for r in caplog.records)


def test_hello_world_non_verbose(caplog: pytest.LogCaptureFixture) -> None:
    """The non-verbose mode logs at ``INFO`` level."""
    with caplog.at_level(logging.INFO, logger="template_python.core"):
        hello_world(verbose=False)
    assert any(r.levelno == logging.INFO and r.message == "Hello World" for r in caplog.records)


@pytest.mark.parametrize(
    ("verbose", "expected_level"),
    [
        (True, logging.DEBUG),
        (False, logging.INFO),
    ],
)
def test_hello_world_parametrized(
    caplog: pytest.LogCaptureFixture,
    verbose: bool,
    expected_level: int,
) -> None:
    """Parametrised verification of the level/message pairing."""
    with caplog.at_level(expected_level, logger="template_python.core"):
        hello_world(verbose=verbose)
    assert any(r.levelno == expected_level and r.message == "Hello World" for r in caplog.records)
