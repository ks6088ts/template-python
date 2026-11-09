"""Process logging configuration for the application boundary."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import override

TEXT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_FORMATS = frozenset({"text", "json"})


class JsonFormatter(logging.Formatter):
    """Render each record as a single-line JSON object for log collectors."""

    @override
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, str] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str, log_format: str = "text") -> None:
    """Configure root logging on stderr; call once at the application boundary."""
    numeric_level = logging.getLevelNamesMapping().get(level.upper())
    if numeric_level is None:
        msg = f"unsupported log level: {level}"
        raise ValueError(msg)
    if log_format not in LOG_FORMATS:
        msg = f"unsupported log format: {log_format}"
        raise ValueError(msg)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter() if log_format == "json" else logging.Formatter(TEXT_FORMAT))
    logging.basicConfig(level=numeric_level, handlers=[handler], force=True)
