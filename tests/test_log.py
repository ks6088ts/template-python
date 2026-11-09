import json
import logging

import pytest

from template_python.log import configure_logging


def test_configure_logging_emits_text_once(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")

    logging.getLogger("template.test").info("ready")

    captured = capsys.readouterr()
    assert captured.err.count("ready") == 1
    assert "[INFO] template.test: ready" in captured.err


def test_configure_logging_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("warning", "json")

    logger = logging.getLogger("template.test")
    logger.info("hidden")
    try:
        raise RuntimeError("boom")  # noqa: TRY301
    except RuntimeError:
        logger.exception("failed")

    lines = capsys.readouterr().err.splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["level"] == "ERROR"
    assert record["logger"] == "template.test"
    assert record["message"] == "failed"
    assert "RuntimeError: boom" in record["exception"]
    assert record["timestamp"].endswith("+00:00")


def test_configure_logging_rejects_unknown_level() -> None:
    with pytest.raises(ValueError, match="unsupported log level"):
        configure_logging("TRACE")


def test_configure_logging_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="unsupported log format"):
        configure_logging("INFO", "xml")
