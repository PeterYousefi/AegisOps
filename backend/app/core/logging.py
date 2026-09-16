"""Structured JSON logging baseline.

Emits one JSON object per log line with a stable, minimal shape suitable for
local development and future Azure Monitor / Application Insights ingestion.

Safety notes:
- This module never logs request bodies, headers (including Authorization),
  cookies, environment contents, or any credentials.
- A per-request correlation ID is attached when available via a contextvar,
  so log lines can be traced without logging sensitive request data.
"""

from __future__ import annotations

import contextvars
import datetime as _dt
import json
import logging
from typing import Any

# Holds the correlation id for the current request/task, if one is set.
correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)


class JsonFormatter(logging.Formatter):
    """Format log records as compact single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = _dt.datetime.fromtimestamp(
            record.created, tz=_dt.timezone.utc
        ).isoformat()

        payload: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        correlation_id = correlation_id_var.get()
        if correlation_id:
            payload["correlation_id"] = correlation_id

        # Include exception info only as a type/message summary, never as a
        # raw stack trace in the structured fields. Standard logging still
        # renders tracebacks to the message when explicitly requested via
        # logger.exception(...); we avoid leaking internals into responses.
        if record.exc_info:
            exc_type = record.exc_info[0]
            payload["error_type"] = getattr(exc_type, "__name__", "Exception")

        return json.dumps(payload, separators=(",", ":"))


def configure_logging(level: str) -> None:
    """Configure the root logger to emit JSON at the given level.

    Idempotent: replaces existing handlers so repeated calls (e.g. across app
    factory invocations in tests) do not stack duplicate handlers.
    """
    root = logging.getLogger()
    root.setLevel(level)

    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
