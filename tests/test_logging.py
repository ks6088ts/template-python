import logging

import pytest

from template_python.logging import configure_logging


def test_configure_logging_emits_once(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")

    logging.getLogger("template.test").info("ready")

    captured = capsys.readouterr()
    assert captured.err.count("ready") == 1


def test_configure_logging_rejects_unknown_level() -> None:
    with pytest.raises(ValueError, match="unsupported log level"):
        configure_logging("TRACE")
