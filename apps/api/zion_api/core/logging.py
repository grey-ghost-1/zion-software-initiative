"""Structured, secret-safe request logging configuration."""

from __future__ import annotations

import logging
import re
from typing import Any

_REDACT_PATTERNS = (
    re.compile(r"(authorization\"?\s*[:=]\s*\"?)(Bearer\s+\S+)", re.IGNORECASE),
    re.compile(r"(password\"?\s*[:=]\s*\"?)([^\s\"&]+)", re.IGNORECASE),
)


def _redact(message: str) -> str:
    for pattern in _REDACT_PATTERNS:
        message = pattern.sub(r"\1[REDACTED]", message)
    return message


class RedactingFilter(logging.Filter):
    """Best-effort defensive redaction of secrets that reach log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _redact(record.msg)
        return True


def configure_logging(log_level: str) -> None:
    """Configure root logging once, with request-safe defaults.

    Only method, path, status code, duration, and request ID are logged for
    each request. Headers, query strings, and bodies are never logged, so
    tokens and passwords cannot leak through access logs.
    """

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s level=%(levelname)s logger=%(name)s message=%(message)s"
        )
    )
    handler.addFilter(RedactingFilter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(log_level.upper())


def access_log_extra(
    *, request_id: str, method: str, path: str, status_code: int, duration_ms: float
) -> dict[str, Any]:
    """Build the safe, structured fields for one access-log line."""

    return {
        "request_id": request_id,
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
