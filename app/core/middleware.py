from collections.abc import Callable
from typing import Awaitable

from fastapi import Request, Response
import time
import logging

logger = logging.getLogger("fitmetrics")

EXCLUDED_PATHS = {"/health"}


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()

    response = await call_next(request)

    if request.url.path not in EXCLUDED_PATHS:
        process_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            process_ms,
        )
    return response
