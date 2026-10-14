"""Typed application errors and their HTTP mapping.

Every error handled here produces a stable, minimal JSON envelope:

```json
{"error": {"code": "invalid_credentials", "message": "...", "request_id": "..."}}
```

No stack trace, header, or internal detail is ever included in a response body.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("zion_api.errors")


class AppError(Exception):
    """Base class for typed, client-facing application errors."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "application_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class InvalidCredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "invalid_credentials"


class InvalidOrExpiredTokenError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "invalid_or_expired_token"


class RoleDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "role_denied"


class OrganizationNotFoundError(AppError):
    """Raised for a missing organization or a non-member.

    Both cases return the same 404 so an unauthorized caller cannot use the
    response to enumerate organizations they do not belong to.
    """

    status_code = status.HTTP_404_NOT_FOUND
    code = "organization_not_found"


def _request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unknown"))


def _error_body(code: str, message: str, request_id: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message, "request_id": request_id}}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach typed error handling to the FastAPI application."""

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, _request_id(request)),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_error_body(
                "validation_error", "The request did not match the expected schema.",
                _request_id(request),
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            extra={"request_id": _request_id(request), "path": request.url.path},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(
                "internal_server_error",
                "An unexpected error occurred.",
                _request_id(request),
            ),
        )
