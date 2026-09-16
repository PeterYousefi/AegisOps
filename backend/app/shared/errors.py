"""Domain error types and FastAPI exception handlers.

Errors are returned in a consistent shape:

    {"error": {"code": "...", "message": "...", "correlation_id": "..."}}

Messages are safe for clients; internal details and stack traces are never
included in responses.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import correlation_id_var
from app.shared.state_machine import InvalidStateTransition


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found") -> None:
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    """Raised when a request is semantically invalid."""

    def __init__(self, message: str = "Invalid request") -> None:
        self.message = message
        super().__init__(message)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "correlation_id": correlation_id_var.get(),
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach domain exception handlers to the FastAPI app."""

    @app.exception_handler(NotFoundError)
    async def _not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return _error_response(404, "not_found", exc.message)

    @app.exception_handler(ValidationError)
    async def _validation(_: Request, exc: ValidationError) -> JSONResponse:
        return _error_response(422, "validation_error", exc.message)

    @app.exception_handler(InvalidStateTransition)
    async def _invalid_transition(
        _: Request, exc: InvalidStateTransition
    ) -> JSONResponse:
        return _error_response(409, "invalid_state_transition", str(exc))
