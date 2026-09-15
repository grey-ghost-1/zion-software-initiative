"""ASGI middleware assigning a per-request correlation ID and safe access log."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from zion_api.core.logging import access_log_extra

logger = logging.getLogger("zion_api.access")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a fresh server-generated request ID to every request/response.

    Incoming client-supplied request-id headers are intentionally ignored so a
    caller cannot inject arbitrary values into logs or correlate across
    unrelated requests.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = uuid.uuid4().hex
        request.state.request_id = request_id
        started = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - started) * 1000
        response.headers[REQUEST_ID_HEADER] = request_id
        logger.info(
            "request_completed",
            extra=access_log_extra(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            ),
        )
        return response
